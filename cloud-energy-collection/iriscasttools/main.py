"""
Collects energy usage metrics using IPMI, as well as other metrics such as CPU and RAM usage.
"""
import utils


def get_iriscast_stats(csv=False, include_header=False):
    """
    Get stats for iriscast

    Keyword arguments:
        csv -- bool, flag to set if output should be formatted as csv or dict
        include_header -- bool, flag to set if header should be included if csv flag set

    """

    all_stats = {}

    power_stats = utils.get_ipmi_power_stats("current_power")

    all_stats.update(power_stats)
    all_stats.update(utils.get_os_load("os_load5"))
    all_stats.update(utils.get_ram_usage("ram_usage_percentage"))

    if csv:
        return utils.to_csv(all_stats, include_header)
    return all_stats
