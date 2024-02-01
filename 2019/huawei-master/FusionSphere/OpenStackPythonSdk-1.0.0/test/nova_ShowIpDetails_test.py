# coding=gbk
import os
import sys
import time

sys.path.append("../third_client")
import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient
import novaclient.client as novaclient
import neutronclient.v2_0.client as netclient
import cinderclient.client as cinclient

username = 'ggldemo'
password = 'Huawei@123'
tenant_name = 'service'
auth_url = 'https://identity.az1.dc1.fusionsphere.com:443/identity/v2.0'
tenant_id = ''
glance_endpoint = ''


server_id = 'afa64307-fe73-4e56-a213-69f1338c5ed0'
networkname = 'mynetworkzzh'

if __name__ == '__main__':
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    networkname1 = 'networkname'

    ips_detail = nova_client.servers.show_ip_details(server_id,networkname1)
    print ips_detail
    print ips_detail[networkname1][0]["version"]
    print ips_detail[networkname1][0]["addr"]


