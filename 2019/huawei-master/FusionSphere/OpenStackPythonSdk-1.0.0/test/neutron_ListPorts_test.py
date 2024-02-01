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
port_name = ''
is_admin_status_up = ''
network_id = ''
port_mac = ''
port_device_id = ''
device_owner = ''
port_status = ''

if __name__ == '__main__':
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)


    port_list = neutron.list_ports(retrieve_all=True,name = port_name, admin_state_up = is_admin_status_up, 
                               network_id = network_id, mac_address = port_mac, device_id = port_device_id, device_owner = device_owner, 
                               tenant_id = tenant_id, status = port_status)

    print port_list

   