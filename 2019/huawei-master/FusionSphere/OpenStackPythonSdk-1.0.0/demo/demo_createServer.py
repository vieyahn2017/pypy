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

def UserAuth():
    global tenant_id,glance_endpoint

    keystone = ksclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)

    tenants = keystone.tenants.list()
    my_tenant = [x for x in tenants if x.name==tenant_name][0]
    tenant_id = my_tenant.id
    print tenant_id

    glance_endpoint = keystone.service_catalog.url_for(service_type='image',endpoint_type='publicURL')

    return keystone.auth_token

def QueryNetwork():
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure=True)

    networks = neutron.list_networks(status='ACTIVE')

    return networks['networks']

def CreateNetwork():
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure = True)

    network = {'name': 'mynetwork0707', 'router:external': True, 'shared': False, 'tenant_id': tenant_id}
    netinfo = neutron.create_network({'network':network})
    return netinfo['network']['id']

def CreateSubNet(network_id):
    neutron = netclient.Client(auth_url = auth_url,username = username,password = password,
                               tenant_name = tenant_name,insecure = True)

    subnet = {'network_id': network_id, 'ip_version':4, 'cidr': '192.168.1.0/24'}
    neutron.create_subnet({'subnet':subnet})

def QueryVolume():
    cinder = cinclient.Client(version = '2',username = username,api_key = password,
                              tenant_id = tenant_id,auth_url = auth_url,insecure = True)

    volumelist = cinder.volumes.list()

    if len(volumelist) == 0:
        return 0,None
    else:
        return len(volumelist),volumelist[0].id

def CreateVolume():
    cinder = cinclient.Client(version = '2',username = username,api_key = password,
                              tenant_id = tenant_id,auth_url = auth_url,insecure = True)

    #50GB
    #myvol = cinder.volumes.create(name="myvol", size=50, description = 'test create volume',
    #                              imageRef=image_id, volume_type = 'type02')
    myvol = cinder.volumes.create(name="myvol", size=50, description = 'test create volume')

    return myvol.id

def print_flavors(flavor_list):
    for flavor in flavor_list:
        print("-"*35)
        print("flavor id : %s" % flavor.id)
        print("flavor name : %s" % flavor.name)
        print("flavor vcpus : %s" % flavor.vcpus)
        print("flavor disk : %s" % flavor.disk)
        print("-"*35)

def QueryFlavors():
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    flavors_list =  nova_client.flavors.list()

    return flavors_list

def CreateFlavors():
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    flavor = nova_client.flavors.create(name='flavorzzh',ram=4096,vcpus=4,disk=60,flavorid="flavorzzh")

    return flavor,flavor.id

def DeleteFlavor():
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    flavor = nova_client.flavors.find(name='flavorzzh')
    nova_client.flavors.delete(flavor)

def print_Images(images_list):
    for image in images_list:
        print("-"*35)
        print("image id : %s" % image.id)
        print("image name : %s" % image.name)
        print("-"*35)

def QueryImage(auth_token):
    glance = glclient.Client(version = '2',endpoint = glance_endpoint, token=auth_token, insecure=True)

    images = glance.images.list()
    image_use_id = None
    image_use = None
    #print_Images(images)

    for image in images:
        if image.name == 'win_7_x64':
            image_use_id = image.id
            image_use = image
            break

    return image_use,image_use_id

def print_Servers(server_list):
    for server in server_list:
        print("-"*35)
        print("server id : %s" % server.id)
        print("server name : %s" % server.name)
        print("status name : %s" % server.status)
        print("-"*35)

def prn_obj(obj):
    print ', '.join(['%s:%s' % item for item in obj.__dict__.items()])

def CreateServer(image,flavor,NetID,VolID):
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)
    #NET
    nic = {}
    nic['net-id'] = NetID

    nics = []
    nics.append(nic)
    

    #VOLUME
    block_device_mapping_v2 = []

    bdm_dict = {'uuid': VolID, 'source_type': 'volume',
                'destination_type': 'volume', 'boot_index': 0,
                'device_name': '/dev/sdb',"delete_on_termination":"false",'volume_size':60}
    block_device_mapping_v2.insert(0, bdm_dict)

    instance = nova_client.servers.create(name = 'zzh_server7', image = None, flavor = flavor, nics = nics,
                                          disk_config = 'AUTO', admin_pass = 'Huawei@123',
                                          block_device_mapping_v2=block_device_mapping_v2,
                                          availability_zone = 'az1.dc1')

    #print type(instance)
    #prn_obj(instance)

    # Poll at 5 second intervals, until the status is no longer 'BUILD'
    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        # Retrieve the instance again so the status field updates
        instance = nova_client.servers.get(instance.id)
        status = instance.status

    #If instance.status is ERROR,may be cause by your cpu.Now RESET server MANUAL
    print "status: %s" % status


def QueryServer():
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    server_list = nova_client.servers.list()

    print_Servers(server_list)

def DeleteServer():
    nova_client = novaclient.Client(version = '2',username = username,api_key = password,
                                    auth_url = auth_url,project_id = tenant_name,insecure = True)

    server_list = nova_client.servers.list()

    nova_client.servers.delete(server_list[0])

if __name__ == '__main__':

    auth_token = UserAuth()

    NetList = QueryNetwork()
    NetID = ''
    
    print len(NetList),type(NetList)

    if len(NetList) == 0:
        NetID = CreateNetwork()

        CreateSubNet(NetID)
    else:
        for network in NetList:
            if network['name'] == 'mynetwork0707':
                NetID = network['id']
                break
        else:
            NetID = CreateNetwork()

            CreateSubNet(NetID)


    VolNum,VolID = QueryVolume()
    if VolNum == 0:
        VolID = CreateVolume()

    flavors_list = QueryFlavors()
    flavor_instance = None
    flavor_id = None
    if len(flavors_list) == 0:
        flavor_instance,flavor_id = CreateFlavors()
    else:
        for flavor in flavors_list:
            if flavor.name == 'flavorzzh':
                flavor_id = flavor.id
                flavor_instance = flavor
                break
        else:
            flavor_instance,flavor_id = CreateFlavors()

#    image_instace,image_id = QueryImage(auth_token)
    image_id=None

    print NetID
    print VolID
    print flavor_id
#    print image_instace,image_id

    CreateServer(image_id,flavor_id,NetID,VolID)

    #QueryServer()

    #DeleteServer()
    print "Finish the job\r\n"
