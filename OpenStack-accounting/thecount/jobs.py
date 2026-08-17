from typing import List, Dict, Any
import logging
from abc import ABC, abstractmethod
from datetime import datetime

from thecount.sink import Sink
from thecount.source import Source

logger = logging.getLogger(__name__)

class Job(ABC):
    """
    Abstract base class for all accounting jobs
    """
    db_name = ""

    def run(
            self,
            source: Source,
            sink: Sink,
            start_time: datetime,
            end_time: datetime,
            dry_run=False
    ) -> None:
        """
        function that fetches data from the source, parses and transforms it, then passes it to the sink
        source: a Source object is configured to fetch accounting data
            - implements the fetch() method
        sink: a Sink object is configured to write transformed/parsed accounting data somewhere
            - implements the write() method
        start_time: python datetime - the start time of the job
        end_time: python datetime - the end time of the job
        dry_run: boolean - whether to run the job in dry run mode - i.e. print to console instead of sending
        it to source (useful for debugging)
        """
        rows = source.fetch(
            database=self.db_name,
            start_time=start_time,
            end_time=end_time,
        )
        out = self._transform(rows, end_time, sink.instance)
        print(out) if dry_run else sink.write(out)

    @staticmethod
    def get_department(result: Dict[str, Any]) -> str:
        """
        helper function returns an appropriate accounting department for each project from source
        """
        department = result["Department"]
        if "rally" in result["Project"]:
            department = "STFC Cloud"
        elif "default" in result["Department"].casefold():
            department = result["Project"]
        return department

    @staticmethod
    @abstractmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance) -> str:
        """ABSTRACT CLASS - to be implemented by subclasses"""
        pass


class CinderAccounting(Job):
    db_name="cinder"

    @staticmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance) -> str:
        """
        transform cinder data from source to get total amount of usage (GB seconds) for block-storage per project
        :rows: list of dictionaries containing cinder data from source database
        :end_time: python datetime - the end time of the job - used to timestamp the entry to sink
        :instance: string annotation to pass to sink to state which source the data came from
        """
        datastring = ""
        for row in rows:
            department = Job.get_department(row).replace(' ', r'\ ')
            project = row['Project'].replace(' ', r'\ ')

            datastring += (
                f"Accounting"
                f",instance={instance}"
                f",AvailabilityZone={row['AvailabilityZone']}"
                f",Project={project}"
                f",Department={department}"
                f",CinderType={row['CinderType']}"
                f",YYYY-MM={end_time.strftime('%Y-%m')}"

                f" Volumes={row['Volumes']}"
                f",Volume_Seconds={row['Volume_Seconds']}"
                f",CinderGBs={row['Volume_GB'] * row['Volume_Seconds'] * row['Volumes']}"

                f" {end_time.timestamp():.0f}\n"
            )
        return datastring


class GlanceAccounting(Job):
    db_name="glance"

    @staticmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance) -> str:
        """
        transform glance data from source to get total image/snapshot storage usage (GB seconds) per project
        :rows: list of dictionaries containing glance data from source database
        :end_time: python datetime - the end time of the job - used to timestamp the entry to sink
        :instance: string annotation to pass to sink to state which source the data came from
        """
        datastring = ""
        for row in rows:
            department = Job.get_department(row).replace(' ', r'\ ')
            project = row['Project'].replace(' ', r'\ ')

            datastring += (
                f"Accounting"
                f",instance={instance}"
                f",Project={project}"
                f",Department={department}"
                f",StorageBackend={row['StorageBackend']}"
                f",GlanceType={row['GlanceType']}"
                f",YYYY-MM={end_time.strftime('%Y-%m')}"

                f" Images={row['Images']}"
                f",Image_Seconds={row['Image_Seconds']}"
                # previous data had 4 decimal places of accuracy
                f",GlanceGBSeconds={row['Glance_GB'] * row['Image_Seconds'] * row['Images']:.4f}"

                f" {end_time.timestamp():.0f}\n"
            )
        return datastring


class ManilaAccounting(Job):
    db_name="manila"

    @staticmethod
    def _transform(rows: List[Dict[str, Any]], end_time: datetime, instance) -> str:
        """
        transform manila data from source to get the total shared network storage used (GB seconds) per project
        :rows: list of dictionaries containing manila data from source database
        :end_time: python datetime - the end time of the job - used to timestamp the entry to sink
        :instance: string annotation to pass to sink to indicate which source the data came from
        """
        datastring = ""
        for row in rows:
            department = Job.get_department(row).replace(' ', r'\ ')
            project = row['Project'].replace(' ', r'\ ')

            datastring += (
                f"Accounting"
                f",instance={instance}"
                f",AvailabilityZone={row['Availability_zone']}"
                f",Project={project}"
                f",Department={department}"
                f",ManilaType={row['ManilaType']}"
                f",ManilaShareType={row['Share_type']}"
                f",YYYY-MM={end_time.strftime('%Y-%m')}"
                
                f" Shares={row['Shares']}"
                f",Share_Seconds={row['Share_Seconds']}"
                f",ManilaGBs={row['Share_GB'] * row['Share_Seconds'] * row['Shares']}"

                f" {end_time.timestamp():.0f}\n"
            )
        return datastring


class NovaAccounting(Job):
    db_name="nova"

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
            department = Job.get_department(row).replace(' ', r'\ ')
            project = row['Project'].replace(' ', r'\ ')

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
