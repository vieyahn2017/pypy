'''
Created on 2016-3-24

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
tenant_id = '629cf1db0818453a9245de9b63ce4bc8'
glance_endpoint = ''

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])
    
if __name__ == '__main__':
    cinder_client = cinclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    metadata={}
    metadata["option"]="MOD"
    metadata["id"]="fb4a80ba07af"
    metadata["desc"]="MOD-volume_GGL001"
    update_volume = cinder_client.volumes.update(volume="c3cab06d-ed6b-42f8-ac90-9e58f8bec7a8", name="testzzh_20160408",description="MOD volume test2",metadata=metadata)

    print update_volume