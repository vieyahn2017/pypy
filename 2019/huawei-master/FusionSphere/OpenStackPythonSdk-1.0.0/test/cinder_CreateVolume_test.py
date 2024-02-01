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

username = 'ggldemo'
password = 'Huawei@123'
tenant_name = 'service'
auth_url = 'https://identity.az1.dc1.fusionsphere.com:443/identity/v2.0'
tenant_id = '629cf1db0818453a9245de9b63ce4bc8'
glance_endpoint = ''

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])
    
if __name__ == '__main__':
    cinder_client = cinclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    volume = cinder_client.volumes.create(size=20,consistencygroup_id=None, snapshot_id=None,
               source_volid="f60abc1c-e500-4b83-a6a6-65931a6ab52e", name="testzzh_20160408_kkl", description='test create volume1',
               volume_type="typesan",
               project_id=tenant_id, availability_zone="az1.dc1",
               metadata=None, imageRef=None, scheduler_hints=None,
               source_replica=None, shareable=True)
    prn_obj(volume)