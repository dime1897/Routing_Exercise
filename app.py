from flask import Flask, render_template, request
from flask_restful import Resource, Api
from wtforms import Form, IntegerField, StringField, validators, SubmitField
from routing import Routing
import ipaddress

class SearchRouting(Form):
    ip = StringField('IP:', [validators.length(max=15)])
    submit = SubmitField('CHECK')
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

app = Flask(__name__,
            static_url_path='/static', 
            static_folder='static')
dao=Routing()

api = Api(app)
basePath = '/api/v1'
rule_fields=['ip', 'netmaskCIDR', 'gw', 'device']

def validate_ip_address(ip:str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False

def validate_rule(rule:dict) -> bool:
    try:
        for field in rule.keys():
            if not field in rule_fields: return False
        if rule['netmaskCIDR']<0: return False
        ipaddress.ip_network(rule['ip']+'/'+str(rule['netmaskCIDR']))
        ipaddress.ip_address(rule['gw'])
        return True
    except:
        return False

class Table_Management(Resource):
    def post(self, id):
        rule = request.json
        try:
            if int(id)<0: return None, 400
        except:
            return None, 400
        if not validate_rule(rule):
            return None, 400
        elif not dao.get_rule(id) is None:
            return None, 409
        else:
            return dao.insert_rule(rule, id), 201
    def get(self, id):
        try:
            if int(id)<0: return None, 400
        except:
            return None, 400
        rule = dao.get_rule(id)
        if not rule is None: return rule, 200
        else: return None, 404
    def put(self, id):
        rule = request.json
        try:
            if int(id)<0: return None, 400
        except:
            return None, 400
        for field in rule.keys():
            if not field in rule_fields: return None, 400
        if dao.get_rule(id) is None: return None, 404
        else: return dao.update_rule(rule,id), 200
    def delete(self, id):
        try:
            if int(id)<0: return None, 404
        except:
            return None, 404
        rule = dao.get_rule(id)
        if rule is None: return None, 404
        dao.delete_rule(id)
        return None, 204
    
class Check_Rules(Resource):
    def post(self):
        ip = request.json
        ip = ip[1:len(ip)-1]
        if validate_ip_address(ip): return dao.verify_rule(ip), 200
        else: return None, 400
    def get(self):
        return dao.get_all_rules(), 200
    
class Clean_DB(Resource):
    def post(self):
        dao.delete_all_rules()
        return None, 200

@app.route(f'{basePath}/route', methods=['GET', 'POST'])
def get_list():
    if request.method == 'GET':
        c={}
        ids = dao.get_all_rules()
        rules = dao.get_all_content()
        cform = SearchRouting(obj=Struct(**c))
        return render_template('/route_list.html', ids = ids, rules = rules, that = -1, form = cform)
    elif request.method == 'POST':
        ids = dao.get_all_rules()
        rules = dao.get_all_content()
        cform = SearchRouting(request.form)
        if not validate_ip_address(cform.ip.data):
            return render_template('/404.html', path="What?"), 404
        rule = dao.verify_rule(cform.ip.data)
        rule = int(rule[1:len(rule)-1])
        return render_template('/route_list.html', ids = ids, rules = rules, that = str(rule), form = cform), 200

api.add_resource(Table_Management, f'{basePath}/routing/<id>')
api.add_resource(Check_Rules, f'{basePath}/routing')
api.add_resource(Clean_DB, f'{basePath}/clean')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)