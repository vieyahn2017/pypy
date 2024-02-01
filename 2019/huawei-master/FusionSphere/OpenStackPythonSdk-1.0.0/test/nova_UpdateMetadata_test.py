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
    metadata["user"]="gugenglian"
    metadata["__bootDev"]="hd"
    metadata["_ha_policy_type"]="remote_rebuild"
    metadata["_ha_policy_time"]="300"
    metadata["__loading_update_driver_image"]="enable"
    metadata["vt_upgrade_tag"]="1"
    metadata["__huawei_reserved:manage_vm_type"]="fusion_manager"
    

    metadata=nova_client.servers.update_meta(server="20611bc4-42c1-4d6e-8796-a90f3faf2546", metadata=metadata)
    print type(metadata)
    prn_obj(metadata)