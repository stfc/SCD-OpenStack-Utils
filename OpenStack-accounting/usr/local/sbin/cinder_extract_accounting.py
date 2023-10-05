#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime
import logging

def main():
    nowtime = time.localtime()
    logger = accountinglib.get_logger("cinder")

    logger.info("Cinder Accounting run start")
    starttime=sys.argv[1]
    logger.info("Start Time = " + starttime)
    endtime=sys.argv[2]
    logger.info("End Time = " + endtime)
    endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
    endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


    results = accountinglib.get_accounting_data("cinder", starttime, endtime, logger)
    datastring = ''
    logger.info(results)
    for result in results:
        logger.info(result)
        department = accountinglib.project_to_department(result)


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

    r = accountinglib.send_to_influx(datastring, logger)

    logger.info(r.text)
    logger.info(r)

if __name__ == "__main__":
    main()
