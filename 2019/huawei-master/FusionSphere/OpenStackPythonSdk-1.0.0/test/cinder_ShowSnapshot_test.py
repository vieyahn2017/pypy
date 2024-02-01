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
snapshot_id='2e7862a5-377f-4675-895c-4b2c296c44fc'

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])

if __name__ == '__main__':
    cinder = cinclient.Client(version = '2', username = username, api_key = password, project_id = tenant_name, 
	auth_url = auth_url, insecure = True)

    snapshot_info = cinder.volume_snapshots.get(snapshot_id)
    
    prn_obj(snapshot_info)