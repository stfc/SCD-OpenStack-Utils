from typing import List, Dict, Any
from datetime import datetime

from thecount.parsers.base_parser import BaseParser


class CinderParser(BaseParser):
    db_name = "cinder"

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
            department = BaseParser.get_department(row).replace(" ", r"\ ")
            project = row["Project"].replace(" ", r"\ ")

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
