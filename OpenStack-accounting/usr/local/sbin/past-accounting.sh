#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation

# helper script for regenerating daily accounting over a period of time

startdate=$1
enddate=$2
enddateepoch=`date -d "$enddate" +%s`
startdateepoch=`date -d "$startdate" +%s`

endtime=$startdate
starttime=`date -d "$startdate" +"%Y-%m-%d %H:%M"`
endtimeepoch=`date -d "$endtime" +%s`

while [[ $endtimeepoch -lt $enddateepoch ]];
do
    starttime=`date -d "$starttime" +"%Y-%m-%d %H:%M"`
    starttimeepoch=`date -d "$starttime" +%s`
    endtime=`date -d "$starttime 1 day" +"%Y-%m-%d %H:%M"`
    endtimeepoch=`date -d "$endtime" +%s`
    echo $starttime
    echo $endtime
    for extractor in $(ls /usr/local/bin/*extract_accounting.py);
    do
        $extractor "$starttime" "$endtime";
    done
    starttime=$endtime
done;
