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


results = accountinglib.get_accounting_data("manila",starttime,endtime)
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

    datastring += ",AvailabilityZone="+result["Availability_zone"]
    datastring += ",Project="+result["Project"].replace(' ','\ ')
    datastring += ",Department="+department.replace(' ','\ ')
    datastring += ",ManilaType="+result["ManilaType"]
    datastring += ",ManilaShareType="+result["Share_type"]
    datastring += ",YYYY-MM="+ endyyyymm
    datastring += " Shares="+str(result["Shares"])
    datastring += ",Share_Seconds="+str(result["Share_Seconds"])
    datastring += ",ManilaGBs="+str(result["Share_GB"] * result['Share_Seconds'])



    datastring += " "+str(int(endtimestamp))
    datastring += "\n"

r = accountinglib.send_to_influx(datastring)

print(r.text)
print(r)
