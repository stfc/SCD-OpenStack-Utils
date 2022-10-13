#!/bin/bash

# helper script for calculating accounting for today

enddate=`date +"%Y-%m-%d %H:%M"`
startdate=`date -d "$enddate 1 day ago" +"%Y-%m-%d %H:%M"`
enddateepoch=`date -d "$enddate" +%s`
startdateepoch=`date -d "$startdate" +%s`

echo $startdate
echo $enddate
/usr/local/bin/extract_accounting.py "$startdate" "$enddate"
