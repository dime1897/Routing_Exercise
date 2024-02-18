from google.cloud import firestore
import ipaddress

class Routing(object):
    def __init__(self):
        self.db=firestore.Client(database='routing')
        #self.cnt = len(self.db.collection('rules').get())

    def insert_rule(self, rule:dict, id:str) -> dict:
        rules_ref = self.db.collection('rules')
        try:
            rules_ref.document(id).set(rule)
            #self.cnt += 1
            return rule
        except Exception as e:
            print("Exception found in: insert_rule() --> {"+str(e)+"}")
            return None
        
    def get_rule(self, id:str) -> dict:
        rules_ref = self.db.collection('rules')
        try:
            rule = rules_ref.document(id).get()
            ret = rule.to_dict() if rule.exists else None
            return ret
        except Exception as e:
            print("Exception found in: get_rule() --> {"+str(e)+"}")
            return None
        
    def update_rule(self, rule:dict, id:str) -> dict:
        rules_ref = self.db.collection('rules')
        try:
            rules_ref.document(id).update(rule)
            return self.get_rule(id)
        except Exception as e:
            print("Exception found in: update_rule() --> {"+str(e)+"}")
            return None
        
    def get_all_rules(self) -> list:
        rules_ref = self.db.collection('rules')
        try:
            rules_list = [str(rule.id) for rule in rules_ref.order_by("netmaskCIDR", direction=firestore.Query.DESCENDING).stream()]
            return rules_list
        except Exception as e:
            print("Exception found in: get_all_rules() --> {"+str(e)+"}")
            return None

    def get_all_content(self) -> list:
        rules_ref = self.db.collection('rules')
        try:
            rules_list = self.get_all_rules()
            content = []
            for id in rules_list:
                content.append(rules_ref.document(id).get().to_dict())
            return content
        except Exception as e:
            print("Exception found in: get_all_content() --> {"+str(e)+"}")
            return None

    def verify_rule(self, ip:str) -> str:
        rules_ref = self.db.collection('rules')
        try:
            rules_list = self.get_all_rules()
            for id in rules_list:
                rule = rules_ref.document(id).get().to_dict() #Existance is guaranted
                if ipaddress.ip_address(ip) in ipaddress.ip_network(rule['ip']+'/'+str(rule['netmaskCIDR'])):
                    return '\"'+id+'\"'
            return None
        except Exception as e:
            print("Exception found in: verify_rule() --> {"+str(e)+"}")
            return None
        
    def delete_rule(self, id:str) -> None:
        rules_ref = self.db.collection('rules')
        try:
            rule = rules_ref.document(id)
            rule.delete()
        except Exception as e:
            print("Exception found in: delete_rule() --> {"+str(e)+"}")
            return None
        
    def delete_all_rules(self) -> None:
        rules_ref = self.db.collection('rules')
        doc_list = rules_ref.list_documents()
        for doc in doc_list:
            doc.delete()
        return None