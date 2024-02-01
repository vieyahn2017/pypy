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

server_id = '12f20f84-8bf3-4ec2-a1f0-1a5dd489b685'

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])


if __name__ == '__main__':
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    nova_client.servers.update(server_id,name = 'zzhserver_mod7')

    server_info = nova_client.servers.get(server_id)
    
    prn_obj(server_info)
