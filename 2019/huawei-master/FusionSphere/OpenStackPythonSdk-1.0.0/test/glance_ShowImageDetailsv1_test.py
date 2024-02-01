import os
import sys
import time

sys.path.append("../third_client")
import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient
import novaclient.client as novaclient
import neutronclient.v2_0.client as netclient
import cinderclient.client as cinclient
import glanceclient.v1.client as gloneclient

username = 'zzh0112'
password = '1qaz!QAZ'
tenant_name = 'tenant-zzh'
auth_url = 'https://identity.az1.dc1.fusionsphere.com:443/identity/v2.0'
image_id = 'da149d99-b252-4164-9d06-32fddbf88d75'

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])

if __name__ == '__main__':
    keystone = ksclient.Client(auth_url = auth_url,username = username,password = password,
                         tenant_name = tenant_name,insecure=True)

    glance_endpoint = keystone.service_catalog.url_for(service_type='image',endpoint_type='publicURL')

    glance = gloneclient.Client(version = '1', endpoint = glance_endpoint, token = keystone.auth_token, insecure=True)
    
    image = glance.images.get(image = image_id)

    prn_obj(image)
