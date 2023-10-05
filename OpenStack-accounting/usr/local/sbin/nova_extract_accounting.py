#!/usr/bin/python3
import accountinglib

import sys
import time
import datetime
import logging

def main():
    nowtime = time.localtime()
    logger = accountinglib.get_logger("nova")

    logger.info("Nova Accounting run start")
    starttime=sys.argv[1]
    logger.info("Start Time = " + starttime)
    endtime=sys.argv[2]
    logger.info("End Time = " + endtime)
    endyyyymm=datetime.datetime.strptime(endtime,"%Y-%m-%d %H:%M").strftime('%Y-%m')
    endtimestamp = time.mktime(datetime.datetime.strptime(endtime, "%Y-%m-%d %H:%M").timetuple())


    results = accountinglib.get_accounting_data("nova", starttime, endtime, logger)
    datastring = ''
    for result in results:
        department = accountinglib.project_to_department(result)

        instancetype=result['Charge_Unit']


        datastring += "Accounting"

        datastring += ",AvailabilityZone="+result["AvailabilityZone"]
        datastring += ",Project="+result["Project"].replace(' ','\ ')
        datastring += ",Department="+department.replace(' ','\ ')
        datastring += ",Flavor="+result["Flavor"].replace('.','_')
        datastring += ",FlavorPrefix="+result["Flavor"].split('.')[0]
        datastring += ",InstanceType="+instancetype
        datastring += ",YYYY-MM="+ endyyyymm
        datastring += ",Charge_Unit="+ result["Charge_Unit"]
        datastring += " VMs="+str(result["VMs"])
        datastring += ",VM_Seconds="+str(result["VM_Seconds"])
        datastring += ",Memory_MB_Seconds="+str(result["Memory_MB"] * result['VM_Seconds'])
        datastring += ",Memory_MBs="+str(result["Memory_MB"] * result["VMs"])
        datastring += ",VCPU_Seconds="+str(result["VCPU"] * result['VM_Seconds'])
        datastring += ",VCPUs="+str(result["VCPU"] * result["VMs"])
        datastring += ",Swap_Seconds="+str(result["Swap"] * result['VM_Seconds'])
        datastring += ",Swaps="+str(result["Swap"] * result["VMs"])
        datastring += ",Root_GB_Seconds="+str(result["Root_GB"] * result['VM_Seconds'])
        datastring += ",Root_GBs="+str(result["Root_GB"] * result["VMs"])
        datastring += ",Ephemeral_GB_Seconds="+str(result["Ephemeral_GB"]  * result['VM_Seconds'])
        datastring += ",Ephemeral_GBs="+str(result["Ephemeral_GB"] * result["VMs"])
        if int( accountinglib.ifnull(result["GPU_Num"],0)) > 0:
            datastring += ",GPU_Seconds="+str(float(result["GPU_Num"]) * float(result['VM_Seconds']))
            datastring += ",GPUs=" + str(float(result["GPU_Num"]) * float(result['VMs']))
            logger.info(result)
            datastring += ",COST=" + str(float(result["GPU_Num"]) * float(result['VM_Seconds']) * float(result["Per_Unit_Cost"]) / float(3600))
        else:
            datastring += ",COST=" + str(float(result["VCPU"]) * float(result['VM_Seconds']) * float(result["Per_Unit_Cost"]) / float(3600))
            datastring += ",GPUs=" + str(0)
            datastring += ",GPU_Seconds=" + str(0)


        datastring += " "+str(int(endtimestamp))
        datastring += "\n"

    r = accountinglib.send_to_influx(datastring, logger)

    logger.info(r.text)
    logger.info(r)

if __name__ == "__main__":
    main()
