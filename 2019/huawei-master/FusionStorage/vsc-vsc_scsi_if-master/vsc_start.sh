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
        printf "%-68s \033[1;32m %s\033[0m \n" "Starting $1" "$2"
    else
        printf "%-68s \033[1;31m %s\033[0m \n" "Starting $1" "$2"
    fi
}

load_ko_and_check()
{
    KO=`echo ${1%.*} | awk -F '/' '{print $NF}'`
    if [ ! -z "$(lsmod |grep -w ${KO})" ];then
        vsc_printf "${1}" "done"
        vsc_log "${1} have been insmod before"
        return 0;
    fi

    insmod $1 $2

    if [ -z "$(lsmod |grep -w ${KO})" ];then
        vsc_printf $1 "failed"
        vsc_log "insmod $1 failed"
        return 1
    fi

    vsc_printf $1 "done"
    vsc_log "Start $1 OK"
    return 0
}

ko_load_main()
{
    if [ $# -gt 0 ];then
	vsc_log "input parameter error"
	exit 1
    fi
    load_ko_and_check vsc_scsi_if.ko
    if [ $? -eq 1 ];then
     	exit 1
    fi  
    load_ko_and_check vsc.ko
    if [ $? -eq 1 ];then
     	exit 1
    fi  
    exit 0
}

ko_load_main $*

echo "                                          " >>${VSC_START_LOG}
echo "                                          " >>${VSC_START_LOG}
echo "                                          " >>${VSC_START_LOG}


