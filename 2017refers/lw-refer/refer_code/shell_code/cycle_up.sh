#!/bin/bash
startTime=080000
perDate=$(date "+%Y%m%d")
isNewDay=1
isFirstTime=1
while true
do
    curTime=$(date "+%H%M%S")
    curDate=$(date "+%Y%m%d")
    dt=`date "+%Y%m%d"`
    if [ "$isNewDay" -eq "1" ]
    then
        if [ "$curTime" -gt "$startTime" ]
        then
            if [ "$isFirstTime" -eq "0" ]
            then
                sh gitpull.sh
                sh allservices.sh

                isFirstTime=1
            fi
            isNewDay=0
        else
            if [ "$isFirstTime" -eq "1" ]
            then
                echo 'New Day: ('$curDate') Task schedule Time: ('$startTime') Waiting...'
                isFirstTime=0
            fi

        fi
    else
       
        if [ "$curDate" -gt "$perDate" ]
        then
            echo 'New Day: ('$curDate') Task schedule Time: ('$startTime') Waiting...'
            isNewDay=1
            perDate=$curDate
        fi
    fi
    sleep 1
done

