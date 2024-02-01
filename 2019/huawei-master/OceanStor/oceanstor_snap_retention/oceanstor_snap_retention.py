#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Purge snapshots according to retention policy."""
#
#
# Toni Comerma
# November 2017
#
# Modificacions
#
# TODO:


import sys
import datetime
import atexit
import getopt

from ConfigParser import SafeConfigParser
from OceanStor import OceanStor, OceanStorError


# Constants


# Globals


def us():
    """Print usage information."""
    print 'oceanstor_snap_retention.py [-h] [-c configfile.ini]'
    print "  -c, --config: config file. Default: oceanstor_snap_retention.ini"
    print "  -h, --help  : This text"


def get_config(c, section, key, default):
    value = default
    try:
        if c.has_option("Default", key):
            value = c.get("Default", key)
        if c.has_option(section, key):
            value = c.get(section, key)
    except:
        print "ERROR: Getting config value. Section: {0}, Value: {1}".\
            format(section, key)
        exit(2)
    try:
        return value
    except:
        print "ERROR: valuen not integer. Section: {0}, Value: {1}".\
            format(section, key)
        exit(3)


def get_filesystems(c):
    fs = []
    for section_name in c.sections():
        if section_name not in ["Connection", "Default"]:
            fs.append(section_name)
    return fs


def in_monthly(date, interval_weekly, interval_montly):
    age = (datetime.datetime.now()-date)
    if age.days > interval_weekly and age.days <= interval_montly:
        return True
    else:
        return False


def last_of_month(date, snapshots):
    for i in snapshots:
        timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
        if (date < timestamp and
           date.month == timestamp.month and
           i['keep'] is True):
            return False
    return True


def in_interval_monthly(i, interval):
    age = datetime.datetime.now()-i
    if age.days > interval:
        return False
    else:
        return True


def in_interval_all(i, interval_all):
    first = datetime.datetime.now()-datetime.timedelta(days=interval_all)
    if i > first:
        return True
    else:
        return False


def in_day_weekly(i, weekday):
    if weekday == datetime.date.weekday(i):
        return True
    else:
        return False


def remove_not_matching_snapshots(snapshots, prefix):
    s = []
    for i in snapshots:
        if i['NAME'].startswith(prefix):
            s.append(i)
    return s


def create_snapshots(num):
    snapshots = []
    for i in range(0, num):
        s = {}
        s['name'] = str(i)
        s['filesystem'] = "FSnfs"
        s['date'] = datetime.datetime.now()-datetime.timedelta(days=i)
        s['keep'] = False
        snapshots.append(s)
    return snapshots


def print_fake_snapshots(snapshots):
    for i in snapshots:
        print "{0} {1}: {2}".format(i[0], i['keep'], i['date'])

def print_snapshots(snapshots):
    print " Snapshots:"
    for i in snapshots:
        timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
        print "   Name:'{1}' Date:{2} Keep:{3}".format(i['ID'],
                                                       i['NAME'],
                                                       timestamp,
                                                       i['keep'])

def main(argv):

    # Parametres
    config_file = 'oceanstor_snap_retention.ini'
    host = None
    system_id = None
    vstoreId = None
    username = None
    password = None
    timeout = 10

    default_dry_run = True
    default_interval_all = 8
    default_interval_weekly = 31
    default_interval_monthly = 90
    default_day_weekly = 6  # Sun
    default_snapshot_prefix = ""

    # Read command line parameters
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
        vstoreId = parser.get("Connection", "vstoreId")
        username = parser.get("Connection", "username")
        password = parser.get("Connection", "password")
        timeout = parser.get("Connection", "timeout")
    except:
        print "ERROR: problems reading connection info fromconfig file: {0}".\
              format(config_file)
        exit(1)
    os = OceanStor(host, system_id, vstoreId, username, password, timeout)

    # Connectar
    if not os.login():
        print 'ERROR: Unable to login'
        sys.exit(3)
    # cleaup if logged in
    atexit.register(os.logout)

    filesystems = get_filesystems(parser)
    # Loop filesystems
    for i in filesystems:
        print "Working on filesystem {0}".format(i)
        interval_all = int(get_config(parser, i,
                                      "interval_all", default_interval_all))
        interval_weekly = int(get_config(parser, i,
                                         "interval_weekly",
                                         default_interval_weekly))
        interval_monthly = int(get_config(parser, i,
                                          "interval_montly",
                                          default_interval_monthly))
        day_weekly = int(get_config(parser, i,
                                    "day_weekly", default_day_weekly))
        dry_run = get_config(parser, i, "dry_run", default_dry_run)
        snapshot_prefix = get_config(parser, i, "snapshot_prefix",
                                     default_snapshot_prefix)
        if dry_run == "True":
            dry_run = True
        else:
            dry_run = False
        print " Parameters:"
        print "   interval_all {0}".format(interval_all)
        print "   interval_weekly {0}".format(interval_weekly)
        print "   interval_monthly {0}".format(interval_monthly)
        print "   day_weekly {0}".format(day_weekly)

        # Get snapshots and remover not matching snapshot_prefix
        snapshots = remove_not_matching_snapshots(os.get_snapshots(i),
                                                  snapshot_prefix)

        # Mark all snapshots as deletable
        for i in snapshots:
            i['keep'] = False

        # Preserve all in interval INT_ALL
        for i in snapshots:
            timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
            if in_interval_all(timestamp, interval_all):
                i['keep'] = True

        # Mark all day_weekly as True
        for i in snapshots:
            timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
            if in_day_weekly(timestamp, day_weekly):
                i['keep'] = True

        # Preserve Last weekly in INT_MONTHLY
        for i in snapshots:
            timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
            if i['keep'] is True:
                if (in_monthly(timestamp, interval_weekly, interval_monthly) and
                   not last_of_month(timestamp, snapshots)):
                    i['keep'] = False

        # Purge older backups
        for i in snapshots:
            timestamp = datetime.datetime.fromtimestamp(int(i['TIMESTAMP']))
            if i['keep'] is True:
                if not in_interval_monthly(timestamp, interval_monthly):
                    i['keep'] = False

        # Print decision
        print_snapshots(snapshots)

        # Apply changes. Delete Snapshots
        if not dry_run:
            print " Deleting snapshots"
            for i in snapshots:
                if i['keep'] is False:
                    print "   Deleting snapshot {0}".format(i['NAME'])
                    try:
                        os.delete_snapshot(i['ID'])
                    except OceanStorError as e:
                        if e.code == 1073754122:
                            print "   - Unable to delete. Used by clone"
                        else:
                            raise e
                else:
                    print "   Keeping snapshot {0}".format(i['NAME'])
        else:
            print " Dry Run: Nothing deleted"

####################################################
# Crida al programa principal
if __name__ == "__main__":
    main(sys.argv[1:])
