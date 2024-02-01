#!/bin/sh
LOG_DIR="/var/log/dsware"
test -d ${LOG_DIR} || mkdir -p ${LOG_DIR}

VSC_START_LOG=${LOG_DIR}/log-vsc.log.0

vsc_log()
{
    echo "At time($(date)):"$1"" >>${VSC_START_LOG}
}


vsc_printf()
{
    if [ $2 = "done" ]; then
        printf "%-68s \033[1;32m %s\033[0m \n" "Shutting down $1" "$2"
    else
        printf "%-68s \033[1;31m %s\033[0m \n" "Shutting down $1" "$2"
    fi
}

rmmod_and_check()
{
    rmmod $1 1>>${VSC_START_LOG} 2>>${VSC_START_LOG}

    KO=${1%.*}

    if [ ! -z "$(lsmod |grep -w ${KO})" ];then
        vsc_printf $1 "failed"
        vsc_log "Shutting down ${KO} failed"
        return 1
    fi

    vsc_printf $1 "done"
    vsc_log "Shutting down ${KO} OK"
    return 0
}


echo "------------------$(date)------------------" >>${VSC_START_LOG}
num=`lsmod | grep -w vsc | grep -v scsi | sed -n 1p| awk '{print $3}'`


if [ "x$num" != "x" ] && [ "$num" != "0" ];then
    echo "can't not stop vsc, dsw user num: $num" >>${VSC_START_LOG}
    exit 1
fi

ko_unload_main()
{
   if [ $# -gt 1 ];then
	vsc_log "input parameter error"
	exit 1
   fi
   if [ "$1" == "hot_patch" ];then
       rmmod_and_check vsc.ko
       if [ $? -eq 1 ];then
     	   exit 1
       fi 
       exit 0 
   fi
   rmmod_and_check vsc.ko
   if [ $? -eq 1 ];then
       exit 1
   fi 
   rmmod_and_check vsc_scsi_if.ko
   if [ $? -eq 1 ];then
       exit 1
   fi
   exit 0
}

ko_unload_main $*

echo "                                           " >>${VSC_START_LOG}
echo "                                           " >>${VSC_START_LOG}
echo "                                           " >>${VSC_START_LOG}
