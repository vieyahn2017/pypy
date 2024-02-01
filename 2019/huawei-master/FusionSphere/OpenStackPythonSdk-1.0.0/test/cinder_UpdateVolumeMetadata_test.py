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
volume_id = 'c3cab06d-ed6b-42f8-ac90-9e58f8bec7a8'
metadata_updateuser = 'xuyimingupdate'
metadata_updatebody = 'metadatabodyupdate'

if __name__ == '__main__':
    cinder = cinclient.Client(version = '2', username = username, api_key = password, project_id = tenant_name, 
	auth_url = auth_url, insecure = True)

    metadata = {}
    metadata["user"] = metadata_updateuser
    metadata["body"] = metadata_updatebody
    metadata["readonly"] = "9999"

    cinder.volumes.set_metadata(volume = volume_id, metadata = metadata)