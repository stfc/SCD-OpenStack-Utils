from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

from thecount.source import Source
from thecount.sink import Sink


class BaseParser(ABC):
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
        dry_run=False,
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
        if dry_run:
            print(out)
        else:
            sink.write(out)

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
