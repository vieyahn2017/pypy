# -*- coding: utf-8 -*-
"""Connect to OceanStor device and get information."""
#
# There are implemented just a few functions for our monitoring needs, but
# the capabilitites are huge. EVERYTHING on an OceanStor can be done using
# the API. If not convinced, connect the browser to the device and fire up
# developer tools. You will see the browser is using the API for doing the
# job.
# Google "Huawei OceanStor REST API" for the documentation
#
# Toni Comerma
# Octubre 2017
#
# Modifications
#
# TODO:
#
import urllib
import urllib2
import ssl
import json
import datetime
import sys
from cookielib import CookieJar
import random

class OceanStorError(Exception):
    """Class for OceanStor derived errors."""

    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An error occured connecting to OceanStor"
        super(OceanStorError, self).__init__(msg)


class OceanStor(object):
    """Class that connects to OceanStor device and gets information."""

    def __init__(self, host, system_id, vstoreId, username, password, timeout):
        self.host = host
        self.system_id = system_id
        self.username = username
        self.password = password
        self.timeout = timeout
        self.vstoreId = vstoreId
        # Create reusable http components
        self.cookies = CookieJar()
        self.ctx = ssl.create_default_context()
        # Ignorar validesa del certificat
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        # Afegir debuglevel=1 a HTTPSHandler per depurar crides
        self.opener = urllib2.build_opener(urllib2.HTTPSHandler(context=self.ctx),
                                           urllib2.HTTPCookieProcessor(self.cookies) )
        self.opener.addheaders = [('Content-Type', 'application/json; charset=utf-8')]

    def query(self, url):
        try:
            response = self.opener.open(url)
            content = response.read()
            response_json = json.loads(content)
            # Comprovar si request ok
            if response_json['error']['code'] != 0:
                raise OceanStorError(
                        "ERROR: Got an error response from system ({0})".
                        format(response_json['error']['code']))
        except Exception as e:
            raise OceanStorError("HTTP Exception: {0}".format(e))
        return response_json

    def login(self):
        try:
            formdata = {"username": self.username,
                        "password": self.password, "scope": "0"}
            url = "https://{0}:8088/deviceManager/rest/{1}/sessions".\
                  format(self.host, self.system_id)
            response = self.opener.open(url, json.dumps(formdata))
            content = response.read()
            response_json = json.loads(content)
            # Comprvar login ok
            if response_json['error']['code'] != 0:
                raise OceanStorError(
                        "ERROR: Got an error response from system ({0})".
                        format(response_json['error']['code']))
            self.iBaseToken = response_json['data']['iBaseToken']
            self.opener.addheaders = [('iBaseToken', self.iBaseToken)]
        except Exception as e:
            raise OceanStorError("HTTP Exception: {0}".format(e))
        return True

    def logout(self):
        try:
            url = "https://{0}:8088/deviceManager/rest/{1}/sessions".\
                  format(self.host, self.system_id)
            delete_data(url)
        except:
            # No error control. We are quitting anyway
            return

    def get_data(self, url):
        try:
            response_json = self.query(url)
            if response_json["error"]["code"] != 0:
                raise OceanStorError("API Error Code: {0}, Description: {1} on {3}".\
                                     format(response_json["error"]["code"],
                                            response_json["error"]["description"],
                                            url))
            if "data" in response_json:
                return response_json["data"]
            else:
                return [None]
        except OceanStorError as e:
            raise e
        except Exception as e:
            raise OceanStorError("HTTP Exception getting data: {0}".format(type(e)))

    def delete_data(self, url):
        try:
            request = urllib2.Request(url)
            request.get_method = lambda: 'DELETE'
            f = self.opener.open(request)
            content = f.read()
            response_json = json.loads(content)
            if response_json["error"]["code"] != 0:
                raise OceanStorError("API Error Code: {0}, Description: {1} on {2}".\
                                     format(response_json["error"]["code"],
                                            response_json["error"]["description"],
                                            url))
            if response_json['data']:
                return response_json["data"]
            else:
                return [None]
        except OceanStorError as e:
            raise e
        except Exception as e:
            raise OceanStorError("HTTP Exception deleting data: {0}".format(sys.exc_info()[0]))

    def post_data(self, url, data):
        try:
            response = self.opener.open(url, json.dumps(data))
            content = response.read()
            response_json = json.loads(content)
            if response_json["error"]["code"] != 0:
                raise OceanStorError("API Error Code: {0}, Description: {1} on {2}".\
                                     format(response_json["error"]["code"],
                                            response_json["error"]["description"],
                                            url))
            if response_json['data']:
                return response_json["data"]
            else:
                return [None]
        except OceanStorError as e:
            raise e
        except Exception as e:
            raise OceanStorError("HTTP Exception posting data: {0}".format(sys.exc_info()[0]))

    def get_share_info(self, filesystem_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFSHARE?".\
            format(self.host, self.system_id)
        url = url + urllib.urlencode({'filter': 'FSID:'+filesystem_id,
                                      "range": "[0-100]",
                                      "vstoreId": self.vstoreId})
        return self.get_data(url)[0]

    def get_clone_info(self, filesystem_name):
        url = "https://{0}:8088/deviceManager/rest/{1}/filesystem?".\
            format(self.host, self.system_id)
        url = url + urllib.urlencode({'filter': 'NAME:'+filesystem_name})
        return self.get_data(url)[0]

    def delete_share(self, share_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFSHARE/{2}?".\
            format(self.host, self.system_id, share_id)
        url = url + urllib.urlencode({"vstoreId": self.vstoreId})
        self.delete_data(url)
        return True

    def delete_clone(self, clone_id):
        if clone_id <= 25:
            print "ALERT: Clone number too low."
            exit(1)
        url = "https://{0}:8088/deviceManager/rest/{1}/filesystem/{2}?".\
            format(self.host, self.system_id, clone_id)
        url = url + urllib.urlencode({"vstoreId": self.vstoreId})
        self.delete_data(url)
        return True

    def create_clone(self, clone_name, filesystem_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/filesystem".\
            format(self.host, self.system_id)
        data = {'NAME': clone_name,
                'ALLOCTYPE': 1,
                'PARENTFILESYSTEMID': filesystem_id,
                'vstoreId': self.vstoreId}
        return self.post_data(url, data)

    def create_share(self, share_name, filesystem_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFSHARE".\
            format(self.host, self.system_id)
        url = url + urllib.urlencode({"vstoreId": self.vstoreId})
        data = {'SHAREPATH': share_name,
                'FSID': filesystem_id,
                'vstoreId': self.vstoreId}
        return self.post_data(url, data)

    def delete_share_permission(self, permission_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFS_SHARE_AUTH_CLIENT/{2}?".\
            format(self.host, self.system_id, permission_id)
        url = url + urllib.urlencode({"vstoreId": self.vstoreId})
        self.delete_data(url)
        return True

    def get_share_permissions(self, share_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFS_SHARE_AUTH_CLIENT?".\
            format(self.host, self.system_id)
        url = url + urllib.urlencode({'filter': 'PARENTID:'+share_id,
                                      "range": "[0-100]",
                                      'vstoreId': self.vstoreId})
        return self.get_data(url)

    def create_share_permission(self, share_id, host, mode):
        url = "https://{0}:8088/deviceManager/rest/{1}/NFS_SHARE_AUTH_CLIENT".\
            format(self.host, self.system_id)
        if mode == "rw":
            accessval = 1
        else:
            accessval = 0
        data = {'NAME': host,
                'ACCESSVAL': accessval,
                'SYNC': 0,
                'ALLSQUASH': 1,
                'ROOTSQUASH': 1,
                'SECURE': 1,
                'PARENTID': share_id,
                'vstoreId': self.vstoreId}
        return self.post_data(url, data)
