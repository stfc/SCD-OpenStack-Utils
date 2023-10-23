#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime
import logging

def main():
    '''Processes accounting from Glance'''
    nowtime = time.localtime()
    logger = accountinglib.get_logger("glance")

    logger.info("Glance Accounting run start")
    starttime=sys.argv[1]
    logger.info("Start Time = " + starttime)
    endtime=sys.argv[2]
    logger.info("End Time = " + endtime)
    endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
    endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


    results = accountinglib.get_accounting_data("glance", starttime, endtime, logger)
    datastring = ''
    logger.info(results)
    for result in results:
        logger.info(result)
        department = accountinglib.project_to_department(result)

        datastring += "Accounting"

        datastring += ",Project="+result["Project"].replace(' ','\ ')
        datastring += ",Department="+department.replace(' ','\ ')
        datastring += ",StorageBackend="+result["StorageBackend"]
        datastring += ",GlanceType="+result["GlanceType"]
        datastring += ",YYYY-MM="+ endyyyymm
        datastring += " Images="+str(result["Images"])
        datastring += ",Image_Seconds="+str(result["Image_Seconds"])
        datastring += ",GlanceGBSeconds="+str(result["Glance_GB"] * result['Image_Seconds'] * result['Images'])



        datastring += " "+str(int(endtimestamp))
        datastring += "\n"

    r = accountinglib.send_to_influx(datastring, logger)

    logger.info(r.text)
    logger.info(r)

if __name__ == "__main__":
    main()
