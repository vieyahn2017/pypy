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
port_id = 'fc478360-a856-477b-8fd8-a2b9945a078c'



if __name__ == '__main__':
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)

    port = neutron.show_port(port = port_id)

    print port
