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

if __name__ == '__main__':
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)

    port = {}

    port['name'] = "testportzzh0325"
    port['admin_state_up'] = True
    port['network_id'] = 'be92934a-dba9-4fdf-9cee-b9772996c5d6'
    port['tenant_id'] = '79de0cb6baa1433dbbc34b5a35d5538f'
    port['device_owner'] = "compute:None"
    port['mac_address'] = "fa:16:3e:39:09:bb"
#    port['qos'] = "629cf1db0818453a9245de9b63ce4bc8"

    fixed_ips = []
    fix_ip_1 = {"subnet_id":"308fa808-646d-4fa2-9800-d5d0bd541d67",
               "ip_address":"192.168.1.34"}
    fixed_ips.append(fix_ip_1)

    fix_ip_2 = {"ip_address":"192.168.1.45"}
    fixed_ips.append(fix_ip_2)

    port['fixed_ips'] = fixed_ips
    port['device_id'] = "test_device_id_8881"

    request = {'port':port}
    neutron.create_port(request)
    





