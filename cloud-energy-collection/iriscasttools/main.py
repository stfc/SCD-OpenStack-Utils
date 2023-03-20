import re
import os
from iriscasttools.utils import ( 
    to_csv,
    check_ipmi_conn,
    get_ipmi_power_stats,
    get_os_load,
    get_ram_usage
)

def get_iriscast_stats(poll_period_seconds=300, csv=False, include_header=False):
    """ get stats for iriscast """

    all_stats = {}
    # get all available power info
    power_stats = get_ipmi_power_stats(
        "current_power",
        "minimum_power_over_sampling_duration",
        "maximum_power_over_sampling_duration",
        "average_power_over_sampling_duration",
        "statistics_reporting_time_period"
    )
    power_stats['watt_hours'] = ''

    if power_stats["current_power"] != '':
        power_stats['watt_hours'] = round(
            int(power_stats['current_power']) * (poll_period_seconds/3600), 3
        )

    all_stats.update(power_stats)
    all_stats.update(get_os_load("os_load1", "os_load5", "os_load15"))
    all_stats.update(get_ram_usage("ram_usage_percentage"))

    if csv:
        return to_csv(stats, include_header)
    return stats
        
def get_cloud_monitoring_stats():
    """ get stats for cloud monitoring """
    all_stats = {}

    power_stats = get_ipmi_power_stats(
        "current_power"
    )

    all_stats.update(power_stats)
    all_stats.update(get_os_load("os_load5"))
    all_stats.update(get_ram_usage("ram_usage_percentage"))

    if csv:
        return to_csv(stats, include_header)
    return stats