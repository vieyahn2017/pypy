'''
Created on 2016-3-22

@author: gWX215268
'''
import os
import sys
import time

sys.path.append("../third_client")
import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient
import novaclient.client as novaclient
import neutronclient.v2_0.client as netclient
import cinderclient.client as cinclient

username = 'zzh0112'
password = '1qaz!QAZ'
tenant_name = 'tenant-zzh'
auth_url = 'https://identity.az1.dc1.fusionsphere.com:443/identity/v2.0'
tenant_id = ''
glance_endpoint = ''

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])
    
if __name__ == '__main__':
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)
    metadata={}
    metadata["user"]="zhuzhihua"
    metadata["id"]="fb4a80ba07af"
    metadata["desc"]="set-metadata"
    metadata["0528"]="0528"
    
    metadata=nova_client.servers.set_meta(server="20611bc4-42c1-4d6e-8796-a90f3faf2546", metadata=metadata)
    prn_obj(metadata)
    