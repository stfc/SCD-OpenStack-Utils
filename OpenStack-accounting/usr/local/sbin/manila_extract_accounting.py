#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime
import logging

def main():
    nowtime = time.localtime()
    logger = accountinglib.get_logger("manila")

    logger.info("Manila Accounting run start")
    starttime=sys.argv[1]
    logger.info("Start Time = " + starttime)
    endtime=sys.argv[2]
    logger.info("End Time = " + endtime)
    endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
    endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


    results = accountinglib.get_accounting_data("manila", starttime, endtime, logger)
    datastring = ''
    logger.info(results)
    for result in results:
        logger.info(result)
        department = accountinglib.project_to_department(result)

        datastring += "Accounting"

        datastring += ",AvailabilityZone="+result["Availability_zone"]
        datastring += ",Project="+result["Project"].replace(' ','\ ')
        datastring += ",Department="+department.replace(' ','\ ')
        datastring += ",ManilaType="+result["ManilaType"]
        datastring += ",ManilaShareType="+result["Share_type"]
        datastring += ",YYYY-MM="+ endyyyymm
        datastring += " Shares="+str(result["Shares"])
        datastring += ",Share_Seconds="+str(result["Share_Seconds"])
        datastring += ",ManilaGBs="+str(result["Share_GB"] * result['Share_Seconds'] * result["Shares"])



        datastring += " "+str(int(endtimestamp))
        datastring += "\n"

    r = accountinglib.send_to_influx(datastring, logger)

    logger.info(r.text)
    logger.info(r)


if __name__ == "__main__":
    main()
