#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Create clones of production filesystem for dev environments."""
#
#
# Toni Comerma
# November 2017
#
# Modificacions
#
# TODO:

import sys
import atexit
import getpass
import getopt
from ConfigParser import SafeConfigParser
from OceanStor import OceanStor


# Constants


# Globals


def us():
    """Print usage information."""
    print 'oceanstor_dev_clones.py [-h] [-c configfile.ini]'
    print "  -c, --config     : config file. Default: oceanstor_dev_clones.ini"
    print "  -h, --help     : This text"


def get_config(c, section, key, default):
    value = default
    try:
        if c.has_option(section, key):
            value = c.get(section, key)
    except:
        print "ERROR: Getting config value. Section: {0}, Value: {1}".\
            format(section, key)
        exit(2)
    return value


def main(argv):

    # Parametres
    config_file = 'oceanstor_dev_clones.ini'
    host = None
    system_id = None
    username = None
    action = None
    permissions = None
    timeout = 10

    try:
        opts, args = getopt.getopt(argv,
                                   "hc:",
                                   ["config="])
    except getopt.GetoptError:
        sys.exit(3)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            us()
            sys.exit()
        elif opt in ("-c", "--config"):
            config_file = arg

    # Load Config File
    try:
        parser = SafeConfigParser()
        parser.read(config_file)
    except:
        print "ERROR: problems reading config file: {0}".format(config_file)
        exit(1)

    # Connect to OceanStor
    try:
        host = parser.get("Connection", "host")
        system_id = parser.get("Connection", "system_id")
        username = parser.get("Connection", "username")
        timeout = parser.get("Connection", "timeout")
        vstoreId = parser.get("Connection", "vstoreId")
    except:
        print "ERROR: problems reading connection info from config file: {0}".\
              format(config_file)
        exit(2)

    try:
        password = getpass.getpass("Enter password for {0}: ".format(username))
    except:
        print "Problem entering password"
    os = OceanStor(host, system_id, vstoreId, username, password, timeout)

    # Connectar
    if not os.login():
        print 'ERROR: Unable to login'
        sys.exit(3)
    # cleaup if logged in
    atexit.register(os.logout)

    filesystems = get_config(parser, "General", "filesystems", None).split(' ')
    hosts = get_config(parser, "General", "hosts", None).split(' ')
    environment = get_config(parser, "General", "environment", None)
    permissions = get_config(parser, "General", "permissions", "rw")
    action = get_config(parser, "General", "action", "delete_create")

    # sanitize environment. Be sure there is no strange chars, spaces, etc
    # Otherwise, could screw things up.
    environment = environment.decode("ascii", "ignore").replace(" ", "")
    if environment is None or environment == "":
        print "Invalid value of environment in config file"
        exit(6)
    if permissions not in ["rw", "ro"]:
        print "Invalid value of permissions in config file. Valid: ro, rw"
        exit(4)
    if action not in ["create", "delete", "delete_create"]:
        print "Invalid value of permissions in config file. " +\
              "Valid: delete_create, create, delete"
        exit(5)

    print "Parameters:"
    print "   Filesystems: {0}".format(filesystems)
    print "   Hosts: {0}".format(hosts)
    print "   Environment: {0}".format(environment)
    print "   Permissions: {0}".format(permissions)
    print "   Action: {0}".format(action)

    # Loop filesystems
    for i in filesystems:
        print "Working on filesystem {0}".format(i)
        # Check if clone exists and delete it
        try:
            c = os.get_clone_info(i + "_" + environment)
            if c is not None:
                print "  Clone {0} exists".format(c['NAME'])
                # Delete share
                s = os.get_share_info(c['ID'])
                print "  Share ({0}) {1} exists".format(
                             s['ID'], s['NAME'])
                if action in ["delete", "delete_create"]:
                    print "  Deleting share"
                    os.delete_share(s['ID'])
                print "  Deleting clone"
                os.delete_clone(c['ID'])
            if action in ["create", "delete_create"]:
                # Create clone
                f = os.get_clone_info(i)
                print "  Filesystem ID: {0}".format(f["ID"])
                print "  Creating clone " + i + "_" + environment
                c = os.create_clone(i + "_" + environment, f['ID'])
                # Modify shares access rights (share is created by default)
                s = os.get_share_info(c['ID'])
                for p in os.get_share_permissions(s['ID']):
                    print "   Deleting share permission for {0} ({1})".\
                            format(p['NAME'], p['ID'])
                    os.delete_share_permission(p['ID'])
                # Creating new permissions
                for p in hosts:
                    print "  Creating share permission for {0}".format(p)
                    os.create_share_permission(s['ID'], p, "rw")
        except Exception as e:
            print e

####################################################
# Crida al programa principal
if __name__ == "__main__":
    main(sys.argv[1:])
