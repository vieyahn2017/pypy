#!/bin/bash
# Author:	Jurij Vasiliev
# Date:		17.04.2018
# Version	1.0.0
#
# This plugin was originally made to check the hardware of IBM V7000 and was developed by Lazzarin Alberto.
# Now it is adapted by Grzegorz Was to check the hardware status of Huawei OceanStor.
# To use it you need to add user and ssh key on the OceanStor and your Linux machine.
# Try to log from linux machine to the OceanStor without password, if it succeeds you can use the plugin.
# The help is included into the script.
#
#
# CHANGELOG
# 1.0.1 18.04.2018
# Minor changes in CRITICAL and WARNING displays
#
# 1.0.0 17.04.2018
# First release after original script rebuild.

ssh=/usr/bin/ssh
exitCode=0

while getopts 'H:U:c:d:h' OPT; do
  case $OPT in
    H)  storage=$OPTARG;;
    U)  user=$OPTARG;;
    c)  command=$OPTARG;;
    h)  help="yes";;
    *)  unknown="yes";;
  esac
done

# usage
HELP="
Check Huawei OceanStor through ssh (GPL licence)
usage: $0 [ -M value -U value -Q command -h ]
syntax:
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
Note :
This check uses ssh protocol.
"

if [ "$hlp" = "yes" -o $# -lt 1 ]; then
  echo "$HELP"
  exit 0
fi

tmp_file=oceanstor_$storage_$command.tmp
outputInfo=""


case $command in
  lslun)
      $ssh $user@$storage 'show lun general' |sed '1,4d' > $tmp_file
      cat_status=$(cat $tmp_file |awk '{printf $6}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: LUN OFFLINE \n"
      else
        outputInfo="$outputInfo OK: All LUNs Online \n"
      fi

      while read line
      do
        lun_name=$(echo "${line}" | awk '{printf $2}')
        lun_status=$(echo "${line}" | awk '{printf $6}')

        if [ $lun_status = "Online" ]; then
          outputInfo="$outputInfo OK: LUN $lun_name status: $lun_status \n"
        else
          outputInfo="$outputInfo ATTENTION: LUN $lun_name status: $lun_status \n"
          exitCode=2
        fi

      done < $tmp_file
      ;;

  lsdisk)
      $ssh $user@$storage 'show disk general' |sed '1,4d' > $tmp_file

      cat_status=$(cat $tmp_file |awk '{printf $3}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: Disk OFFLINE \n"
      else
        outputInfo="$outputInfo OK: Disk \n"
      fi

      drive_total=$(/bin/cat $tmp_file |/usr/bin/wc -l)
      while read line
      do
        drive_n=$(echo "${line}" | awk '{printf $1}')
        drive_status=$(echo "${line}" | awk '{printf $3}')
        drive_role=$(echo "${line}" | awk '{printf $6}')
        drive_type=$(echo "${line}" | awk '{printf $4}')
        drive_capacity=$(echo "${line}" | awk '{printf $5}')
        drive_slot=$(echo "${line}" | awk '{printf $1}')

        if [ $drive_status = "Online" ]; then
          outputInfo="$outputInfo OK: Disk $drive_n is online \n"
        else
          outputInfo="$outputInfo ATTENTION: Disk $drive_n \nstatus: $disk_status \nrole: $drive_role \ntype: $drive_type \ncapacity: $drive_capacity \nenclosure: $drive_enclosure \nslot: $drive_slot "
          exitCode=2
        fi

      done < $tmp_file

      ;;

  lsdiskdomain)
      $ssh $user@$storage 'show disk_domain general' |sed '1,4d' > $tmp_file
      cat_status=$(cat $tmp_file |awk '{printf $4}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: DISK DOMAIN OFFLINE \n"
      else
        outputInfo="$outputInfo OK: All DISK DOMAINs Online \n"
      fi

      while read line
      do
        disk_domain_name=$(echo "${line}" | awk '{printf $2}')
        disk_domain_status=$(echo "${line}" | awk '{printf $4}')

        if [ $disk_domain_status = "Online" ]; then
          outputInfo="$outputInfo OK: DISK DOMAIN $disk_domain_name status: $disk_domain_status \n"
        else
          outputInfo="$outputInfo ATTENTION: DISK DOMAIN $disk_domain_name status: $disk_domain_status \n"
          exitCode=2
        fi

      done < $tmp_file
      ;;

  lsenclosure)
      $ssh $user@$storage 'show enclosure' |sed '1,4d' > $tmp_file
      sed -i -e "s/Expansion Enclosure/ExpansionEnclosure/g" $tmp_file

      cat_status=$(cat $tmp_file |awk '{printf $4}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: Enclosure OFFLINE \n"
      else
        outputInfo="$outputInfo OK: Enclosure \n"
      fi

      while read line
      do
        enc_n=$(echo "${line}" | awk '{printf $1}')
        enc_status=$(echo "${line}" | awk '{printf $4}')
        enc_health=$(echo "${line}" | awk '{printf $3}')

        if [ $enc_status = "Online" ]; then
          outputInfo="$outputInfo OK: Enclosure $enc_n status: $enc_status \n"
        else
          outputInfo="$outputInfo ATTENTION: Enclosure $enc_n status: $enc_status \n"
          exitCode=2
        fi

      done < $tmp_file
      ;;

  lsinitiator)
      $ssh $user@$storage 'show initiator' |sed '1,4d' > $tmp_file
      cat_status=$(cat $tmp_file |awk '{printf $2}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: INITIATOR OFFLINE \n"
      else
        outputInfo="$outputInfo OK: All INITIATORs Online \n"
      fi

      while read line
      do
        initiator_name=$(echo "${line}" | awk '{printf $4}')
        initiator_status=$(echo "${line}" | awk '{printf $2}')

        if [ $initiator_status = "Online" ]; then
          outputInfo="$outputInfo OK: INITIATOR $initiator_name status: $initiator_status \n"
        else
          outputInfo="$outputInfo ATTENTION: INITIATOR $initiator_name status: $initiator_status \n"
          exitCode=2
        fi

      done < $tmp_file
      ;;

  lsstoragepool)
      $ssh $user@$storage 'show storage_pool general' |sed '1,4d' > $tmp_file
      cat_status=$(cat $tmp_file |awk '{printf $5}' |grep -i Offline)
      if [ "$?" -eq "0" ]; then
        outputInfo="$outputInfo CRITICAL: STORAGE POOL OFFLINE \n"
      else
        outputInfo="$outputInfo OK: All STORAGE POOLs Online \n"
      fi

      while read line
      do
        spool_name=$(echo "${line}" | awk '{printf $2}')
        spool_status=$(echo "${line}" | awk '{printf $5}')

        if [ $spool_status = "Online" ]; then
          outputInfo="$outputInfo OK: STORAGE POOL $spool_name status: $spool_status \n"
        else
          outputInfo="$outputInfo ATTENTION: STORAGE POOL $spool_name status: $spool_status \n"
          exitCode=2
        fi

      done < $tmp_file
      ;;

    *)
      echo -ne "Command not found. \n"
      exit 3
    ;;
esac

rm $tmp_file
echo -ne "$outputInfo\n"
