#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime


nowtime = time.localtime()

print("Cinder Accounting run start")
starttime=sys.argv[1]
print("Start Time = " + starttime)
endtime=sys.argv[2]
print("End Time = " + endtime)
endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


results = accountinglib.get_accounting_data("cinder",starttime,endtime)
datastring = ''
print(results)
for result in results:
    print(result)
    try:
        if "rally" in result["Project"] :
            department="STFC Cloud"
        else:
            if "default" in result["Department"]:
                department=result["Project"]
            else:
                department=result["Department"]

    except:
        department="UNKNOWN"

    datastring += "Accounting"

    datastring += ",AvailabilityZone="+result["AvailabilityZone"]
    datastring += ",Project="+result["Project"].replace(' ','\ ')
    datastring += ",Department="+department.replace(' ','\ ')
    datastring += ",CinderType="+result["CinderType"]
    datastring += ",YYYY-MM="+ endyyyymm
    datastring += " Volumes="+str(result["Volumes"])
    datastring += ",Volume_Seconds="+str(result["Volume_Seconds"])
    datastring += ",CinderGBs="+str(result["Volume_GB"] * result['Volume_Seconds'] * result["Volumes"])



    datastring += " "+str(int(endtimestamp))
    datastring += "\n"

r = accountinglib.send_to_influx(datastring)

print(r.text)
print(r)
