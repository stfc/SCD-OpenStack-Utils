from typing import List, Dict, Any
from datetime import datetime

from thecount.parsers.base_parser import BaseParser


class NovaParser(BaseParser):
    db_name = "nova"

    @staticmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance) -> str:
        """
        transform nova data from source to get total cost for running VMs on the cloud per project
        - including flavor cost calculations and GPU cost calculations
        :rows: list of dictionaries containing nova data from source database
        :end_time: python datetime - the end time of the job - used to timestamp the entry to sink
        :instance: string annotation to pass to sink to indicate which source the data came from
        """
        datastring = ""
        for row in rows:
            department = BaseParser.get_department(row).replace(" ", r"\ ")
            project = row["Project"].replace(" ", r"\ ")

            # pylint: disable=too-many-locals
            # this is a complicated transform function,
            # using lots of local variables makes it easier to understand
            instancetype = row["Charge_Unit"]
            gpu_num = int(row["GPU_Num"] or 0)
            vm_seconds = int(row["VM_Seconds"])
            vms = int(row["VMs"])
            vcpu = int(row["VCPU"])
            swap = int(row["Swap"])
            root_gb = int(row["Root_GB"])
            ephemeral_gb = int(row["Ephemeral_GB"])
            cost = float(
                gpu_num * vm_seconds * float(row["Per_Unit_Cost"]) / 3600
                if gpu_num > 0
                else vcpu * vm_seconds * float(row["Per_Unit_Cost"]) / 3600
            )

            datastring += (
                f"Accounting"
                f",instance={instance}"
                f",AvailabilityZone={row['AvailabilityZone']}"
                f",Project={project}"
                f",Department={department}"
                f",Flavor={row['Flavor'].replace('.', '_')}"
                f",FlavorPrefix={row['Flavor'].split('.')[0]}"
                f",InstanceType={instancetype}"
                f",YYYY-MM={end_time:%Y-%m}"
                f",Charge_Unit={row['Charge_Unit']}"
                f" VMs={vms}"
                f",VM_Seconds={vm_seconds}"
                f",Memory_MB_Seconds={row['Memory_MB'] * vm_seconds}"
                f",Memory_MBs={row['Memory_MB'] * vms}"
                f",VCPU_Seconds={vcpu * vm_seconds}"
                f",VCPUs={vcpu * vms}"
                f",Swap_Seconds={swap * vm_seconds}"
                f",Swaps={swap * vms}"
                f",Root_GB_Seconds={root_gb * vm_seconds}"
                f",Root_GBs={root_gb * vms}"
                f",Ephemeral_GB_Seconds={ephemeral_gb * vm_seconds}"
                f",Ephemeral_GBs={ephemeral_gb * vms}"
                f",COST={cost}"
                f",GPUs={gpu_num * vms}"
                f",GPU_Seconds={gpu_num * vm_seconds}"
                f" {end_time.timestamp():.0f}\n"
            )
        return datastring
