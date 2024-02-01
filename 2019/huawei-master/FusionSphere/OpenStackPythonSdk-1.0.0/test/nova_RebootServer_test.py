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

server_id = 'afa64307-fe73-4e56-a213-69f1338c5ed0'

REBOOT_SOFT, REBOOT_HARD = 'SOFT', 'HARD'

if __name__ == '__main__':
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

#    server = nova_client.servers.get(server_id)

    nova_client.servers.reboot(server_id,reboot_type=REBOOT_SOFT)
    #nova_client.servers.reboot(server,reboot_type=REBOOT_HARD)
