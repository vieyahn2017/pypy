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

port_id = '339c2755-4295-478e-aeaf-2d177ed48f5d'

if __name__ == '__main__':
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)

    port = {}

    port['name'] = "testportzzh2"
    port['admin_state_up'] = True
    port['device_owner'] = 'Compute:None'
    port['mac_address'] = 'fa:16:3e:06:15:90'
#    port['qos'] = "629cf1db0818453a9245de9b63ce4bc8"

    request = {'port':port}
    neutron.update_port(port=port_id,body=request)


