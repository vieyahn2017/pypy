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
from cookielib import CookieJar


class OceanStorError(Exception):
    """Class for OceanStor derived errors."""

    def __init__(self, code, msg=None):
        self.code = code
        self.msg = msg
        if msg is None:
            # Set some default useful error message
            self.msg = "An error occured connecting to OceanStor"
        super(OceanStorError, self).__init__(msg)


class OceanStor(object):
    """Class that connects to OceanStor device and gets information."""

    def __init__(self, host, system_id, vstoreId, username, password, timeout):
        self.host = host
        self.system_id = system_id
        self.vstoreId = vstoreId
        self.username = username
        self.password = password
        self.timeout = timeout
        # Create reusable http components
        self.cookies = CookieJar()
        self.ctx = ssl.create_default_context()
        # Ignorar validesa del certificat
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        # Afegir debuglevel=1 a HTTPSHandler per depurar crides
        self.opener = urllib2.build_opener(urllib2.HTTPSHandler(context=self.ctx),
                                           urllib2.HTTPCookieProcessor(self.cookies))
        # self.opener = urllib2.build_opener(urllib2.HTTPSHandler(),
        #                                   urllib2.HTTPCookieProcessor(self.cookies))
        self.opener.addheaders = [('Content-Type', 'application/json; charset=utf-8')]


    def date_to_human(self, timestamp):
        return datetime.datetime.fromtimestamp(
                        int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    def query(self, url):
        try:
            response = self.opener.open(url)
            content = response.read()
            response_json = json.loads(content)
            # Comprovar si request ok
            if response_json['error']['code'] != 0:
                raise OceanStorError(response_json['error']['code'],
                        "ERROR: Got an error response from system ({0})".
                        format(response_json['error']['code']))
        except Exception as e:
            raise OceanStorError("HTTP Exception: {0}".format(e))
        return response_json

    def delete_data(self, url):
        try:
            request = urllib2.Request(url)
            request.get_method = lambda: 'DELETE'
            f = self.opener.open(request)
            content = f.read()
            response_json = json.loads(content)
            if response_json["error"]["code"] != 0:
                raise OceanStorError(response_json['error']['code'],
                            "API Error Code: {0}, Description: {1} on {2}".\
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
            raise OceanStorError(0, "HTTP Exception deleting data: {0}".format(sys.exc_info()[0]))

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
                raise OceanStorError(response_json['error']['code'],
                        "ERROR: Got an error response from system ({0})".
                        format(response_json['error']['code']))
            self.iBaseToken = response_json['data']['iBaseToken']
            self.opener.addheaders = [('iBaseToken', self.iBaseToken)]
        except Exception as e:
            raise OceanStorError(0,"HTTP Exception: {0}".format(e))
        return True

    def logout(self):
        try:
            url = "https://{0}:8088/deviceManager/rest/{1}/sessions".\
                  format(self.host, self.system_id)
            request = urllib2.Request(url)
            request.get_method = lambda: 'DELETE'
            f = self.opener.open(request)
            content = f.read()
        except:
            # No error control. We are quitting anyway
            return

    def get_filesystemid(self, filesystem):
        try:
            url = "https://{0}:8088/deviceManager/rest/{1}/filesystem?".\
                  format(self.host, self.system_id)
            url = url + urllib.urlencode({'filter': 'NAME:{0}'.
                                          format(filesystem)})
            response_json = self.query(url)
            # Check name not a substring
            for i in response_json["data"]:
                if (i["NAME"] == filesystem):
                    if i["ISCLONEFS"] == "false":
                        return i["ID"]
        except OceanStorError as e:
            raise e
        except Exception as e:
            raise OceanStorError("HTTP Exception: {0}".format(e))
        return None

    def get_snapshots(self, filesystem):
        try:
            fs = self.get_filesystemid(filesystem)
            if (fs is not None):
                url = "https://{0}:8088/deviceManager/rest/{1}/FSSNAPSHOT?".\
                    format(self.host, self.system_id)
                url = url + urllib.urlencode({'sortby': 'TIMESTAMP,d',
                                              'PARENTID': format(fs)})
                response_json = self.query(url)
                return response_json["data"]
        except OceanStorError as e:
            raise e
        except Exception as e:
            raise OceanStorError("HTTP Exception: {0}".format(e))
        return None

    def delete_snapshot(self, snapshot_id):
        url = "https://{0}:8088/deviceManager/rest/{1}/FSSNAPSHOT/{2}?".\
            format(self.host, self.system_id, snapshot_id)
        url = url + urllib.urlencode({"vstoreId": self.vstoreId})
        self.delete_data(url)
        return True
