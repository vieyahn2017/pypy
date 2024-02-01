# PLUGIN IS STILL IN DEVELOPMENT


# Check Huawei OceanStor nagios plugin
Plugin is a rework of the IBM v7000 - v7000 Unified plugin.\
Original link:\
https://exchange.nagios.org/directory/Plugins/Hardware/Storage-Systems/SAN-and-NAS/IBM-San-Volume-Controller/IBM-v7000--2D-v7000-Unified/details

It is adapted to serve as a hardware check of the Huawei OceanStor and was tested on OceanStor 2600V3.

### PLEASE HAVE IN MIND THAT YOU STILL BETTER IMPLEMENT E-MAIL ALARMS ON THE STORAGE ITSELF!

# Installation
1. Make user on the Huawei OceanStor with read-only privileges.
2. Add public ssh key through CLI to the user on OceanStor with the command: ```change user_ssh_auth_info general user_name=your_username auth_mode=publickey```
3. It will ask for the public key, copy and paste it.
4. Make sure that user which will execute script has private key.
5. Try to execute script as user which will be checking the storage system (instructions below in Usage section)
6. Profit :)

# Usage
Remember to ssh from this user account which will be checking the storage system.
```
# su - nagios
Last login: Wed Apr 18 09:02:21 CEST 2018 on pts/0
-bash-4.2$ /usr/local/bin/check_huawei_oceanstor.sh -H 192.168.1.100 -U nagios -c lsinitiator
The authenticity of host '192.168.1.100 (192.168.1.100)' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ECDSA key fingerprint is MD5xxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.1.100' (ECDSA) to the list of known hosts.

CRITICAL: INITIATOR OFFLINE 
 ATTENTION: INITIATOR host-1-port1 status: Offline 
 ATTENTION: INITIATOR host-1-port2 status: Offline 
 
-bash-4.2$

```


```
/path/to/script/check_huawei_oceanstor.sh -H [host name/ip address] -U [user defined on OceanStor] -c [one of{lslun, lsdisk, lsdiskdomain, lsenclosure, lsinitiator, lsstoragepool}] [-h prints help]

-H --> IP Address
-U --> user
-c --> command to storage
   lslun - show lun general status
   lsdisk - show disk general status
   lsdiskdomain - show disk_domain general status
   lsenclosure - show enclosure status
   lsinitiator - show initiator status (prints alias name for initiator)
   lsstoragepool - show storage_pool general status
-h --> Print this help screen
```

# TODO List
- [ ] Add Health Status check to lsdisk {Normal,Pre-fail}
- [ ] Add SSH known hosts check
