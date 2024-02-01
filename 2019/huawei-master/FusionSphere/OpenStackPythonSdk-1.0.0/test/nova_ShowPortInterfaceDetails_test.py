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

    interface=nova_client.servers.interface_show(server="2425b3d5-ce92-4566-9667-efde65c71c3c", port_id="31ff7c32-7151-450b-a289-45ff35855e6e")
    print type(interface)
    prn_obj(interface)
