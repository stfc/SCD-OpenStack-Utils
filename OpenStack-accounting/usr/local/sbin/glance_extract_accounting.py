#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime


nowtime = time.localtime()

print("Glance Accounting run start")
starttime=sys.argv[1]
print("Start Time = " + starttime)
endtime=sys.argv[2]
print("End Time = " + endtime)
endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


results = accountinglib.get_accounting_data("glance",starttime,endtime)
datastring = ''
print(results)
for result in results:
    print(result)
    try:
        if "rally" in result["Project"] :
            department="STFC Cloud"
        else:
            if "efault" in result["Department"]:
                department=result["Project"]
            else:
                department=result["Department"]

    except:
        department="UNKNOWN"

    datastring += "Accounting"

    datastring += ",Project="+result["Project"].replace(' ','\ ')
    datastring += ",Department="+department.replace(' ','\ ')
    datastring += ",GlanceType="+result["GlanceType"]
    datastring += ",YYYY-MM="+ endyyyymm
    datastring += " Images="+str(result["Images"])
    datastring += ",Image_Seconds="+str(result["Image_Seconds"])
    datastring += ",GlanceGBSeconds="+str(result["Glance_GB"] * result['Image_Seconds'] * result['Images'])



    datastring += " "+str(int(endtimestamp))
    datastring += "\n"

r = accountinglib.send_to_influx(datastring)

print(r.text)
print(r)
