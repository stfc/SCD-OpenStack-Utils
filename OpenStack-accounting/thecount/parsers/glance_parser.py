from typing import List, Dict, Any
from datetime import datetime

from thecount.parsers.base_parser import BaseParser


class GlanceParser(BaseParser):
    db_name = "glance"

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
            department = BaseParser.get_department(row).replace(" ", r"\ ")
            project = row["Project"].replace(" ", r"\ ")

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
