#!/bin/bash

# helper script for regenerating daily accounting over a period of time

startdate=$1
enddate=$2
enddateepoch=`date -d "$enddate" +%s`
startdateepoch=`date -d "$startdate" +%s`

endtime=$startdate
starttime=`date -d "$startdate" +"%Y-%m-%d %H:%M"`


while [ $endtimeepoch -lt $enddateepoch ];
do
    starttime=`date -d "$starttime" +"%Y-%m-%d %H:%M"`
    starttimeepoch=`date -d "$starttime" +%s`
    endtime=`date -d "$starttime 1 day" +"%Y-%m-%d %H:%M"`
    endtimeepoch=`date -d "$endtime" +%s`
    echo $starttime
    echo $endtime
    /usr/local/bin/extract_accounting.py "$starttime" "$endtime"
    starttime=$endtime
done;
