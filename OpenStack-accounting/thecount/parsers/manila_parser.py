from typing import List, Dict, Any
from datetime import datetime

from thecount.parsers.base_parser import BaseParser


class ManilaParser(BaseParser):
    db_name = "manila"

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
            department = BaseParser.get_department(row).replace(" ", r"\ ")
            project = row["Project"].replace(" ", r"\ ")

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
