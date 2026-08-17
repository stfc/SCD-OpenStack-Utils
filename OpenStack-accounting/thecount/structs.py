from dataclasses import dataclass
from typing import List, Optional

from datetime import datetime, timedelta
from thecount.sink import Sink
from thecount.source import Source
from thecount.jobs import Job

@dataclass
class RunDetails:
    """
    create a dataclass to hold accounting run details
    :param jobs: which jobs to run
    :sink: Sink object used to write to influxdb
    :source: Source object used to read data from openstack sql db
    :interval: timedelta object - size of window to collate accounting info between
    :dry_run: bool - if True, will not write to Sink, output to console instead - for testing
    """
    jobs: List[Job]
    sink: Sink
    source: Source
    interval: timedelta
    start_time: datetime
    end_time: Optional[datetime]
    dry_run: bool = False
