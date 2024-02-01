import requests,json
from requests import Session
requests.packages.urllib3.disable_warnings()

def token2json(token):
    with open("token.json","w") as f:
        json.dump(token,f)

def json2token():
    with open("token.json","r") as f:
        token = json.load(f)
        return token

class FusionStorage(object):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.session = Session()
        self.session.headers = {"Content-type": "application/json"}
        self.session.verify = False

    def testToken(self):
        try:
            token = json2token()
            self.session.headers.update(token)
            url = f"https://{self.host}:{self.port}/api/v2/aa/current_sessions"
            response = self.session.get(url)
            data = response.json()
            if data['data']:
                return True
            else:
                return False
        except:
            return False
    def login(self):
        global Token
        url = f"https://{self.host}:{self.port}/api/v2/aa/sessions"
        date = {"username":self.username,"password":self.password}
        try:
            response = self.session.post(url, json=date)
            Token = response.json()["data"]["x_auth_token"]
            self.session.headers.update({"X-Auth-Token":Token,"Content-type": "application/json","Accept-Language":"zh"})
            js_token = {"X-Auth-Token":Token}
            token2json(js_token)
            return True
        except:
            return False
    def get_ALLNodeIpInfo(self):
        url = f"https://{self.host}:{self.port}/dsware/service/resource/queryDswareAllNodeIpInfo"
        response = self.session.get(url)
        data = response.json()
        return data
    def get_volumes(self):
        url = f"https://{self.host}:{self.port}/api/v2/cluster/servers"
        response = self.session.get(url)
        data = response.json()
        return data
    def get_cluster_performance(self):
        jsData = {"objects":[{"object_type": 57347,"indicators": [123,124]}],"break_point": True}
        url = f"https://{self.host}:{self.port}/api/v2/pms/performance_data"
        response = self.session.post(url,json=jsData)
        data = response.json()
        return data
    def get_disk_performance(self):
        jsData = {"objects":[{"object_type": 10,"indicators": [123,124]}],"break_point": True}
        url = f"https://{self.host}:{self.port}/api/v2/pms/performance_data"
        response = self.session.post(url,json=jsData)
        data = response.json()
        return data
    def get_pool_info(self):
        url = f"https://{self.host}:{self.port}/dsware/service/resource/queryStoragePool"
        response = self.session.get(url)
        data = response.json()
        return data
    def get_MessageVersion(self):
        url = f"https://{self.host}:{self.port}/dsware/service/upgrade/queryMessageVersion"
        response = self.session.get(url)
        data = response.json()
        return data
    def get_disk_info(self):
        url = f"https://{self.host}:{self.port}/dsware/service/resource/diskStatistics"
        resopnse = self.session.get(url)
        data = resopnse.json()
        return data
    def get_node_info(self):
        url = f"https://{self.host}:{self.port}/dsware/service/getNodeInfoForHealthCheckTool"
        response = self.session.get(url)
        data = response.json()
        return data
    def get_account(self): #获取用户列表，最大获取1000/页
        url = f"https://{self.host}:{self.port}/dfv/service/obsPOE/account?range=" + '{"offset":0,"limit":1000}'
        response = self.session.get(url)
        data = response.json()
        return data

    def get_account_info(self,account_name):
        result = []
        name_list = account_name
        for name in name_list:
            accountStoragePolicy_url = f"https://{self.host}:{self.port}/dfv/service/obsPOE/accountStoragePolicy/"+f"{name}"
            accountStatistic_url = f"https://{self.host}:{self.port}/dfv/service/obsPOE/accountStatistic/"+f"{name}"
            accountStoragePolicy_response = self.session.get(accountStoragePolicy_url)
            accountStoragePolicy = accountStoragePolicy_response.json()
            accountStatistic_response = self.session.get(accountStatistic_url)
            accountStatistic = accountStatistic_response.json()
            result.append({"accountId":name,
                            "quotaCapacity":accountStoragePolicy.get('data').get('quotaCapacity'),
                            "SpaceSize":accountStatistic.get('data').get('SpaceSize'),
                            "Quota":accountStatistic.get('data').get('Quota'),
                            "BucketCount":accountStatistic.get('data').get('BucketCount'),
                            "ObjectCount":accountStatistic.get('data').get('ObjectCount')})
        return result
    def logout(self):
        token = self.session.headers.get("X-Auth-Token")
        url = f"https://{self.host}:{self.port}/api/v2/aa/sessions" + token
        self.session.delete(url)
        session_url = f"https://{self.host}:{self.port}/api/v2/aa/sessions"
        self.session.delete(session_url)
        self.session.close()
