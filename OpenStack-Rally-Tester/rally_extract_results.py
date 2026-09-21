import sys
from typing import Union, Dict, List
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError

from utils import load_data, load_config, create_metric, add_tags, is_workhour

TIMEOUT = 30  # how long to wait to connect to influxdb before timing out (in seconds)


def create_metrics(data: Union[Dict, List[Dict]]) -> List[Dict]:
    """Convert rally data into a list of metrics."""

    # if only one rally metric is found
    if isinstance(data, dict):
        return [
            create_metric(
                measurement=key,
                fields={"success": 0},
            )
            for key in data
        ]

    # if a list of rally metrics are found
    metrics = []
    for test in data:
        measurement = test["key"]["name"]

        for result in test["result"]:
            fields = {
                "success": int(all(sla["success"] for sla in test["sla"])),
                "duration": result["duration"],
                **result["atomic_actions"],
                "timestamp": result["timestamp"],
            }

            if measurement == "VMTasks.boot_runcommand_delete":
                fields.update({
                    "image": f'"{test["key"]["kw"]["args"]["image"]["name"]}"',
                    "network": f'"{test["key"]["kw"]["args"]["fixednetwork"]}"',
                })

            metrics.append(
                create_metric(
                    measurement=measurement,
                    fields=fields,
                )
            )
    return metrics


def metrics_to_string(metrics: Dict) -> str:
    """Convert metrics to the required output format."""
    lines = []

    for metric in metrics:
        measurement = metric["measurement"].replace(".", "-")
        instance = metric["tags"]["instance"]

        for field, value in metric["fields"].items():
            field = field.replace(".", "-")

            lines.append(
                f"{measurement},"
                f"instance={instance},"
                f"workhours={is_workhour()} "
                f"{field}={value}"
            )

    return "\n".join(lines) + "\n"


def main():
    config = load_config("config.ini")

    influx_client = InfluxDBClient(
        host=config["host"],
        port=config["port"],
        username=config["username"],
        password=config["password"],
        database=config["database"],
        ssl=True,
        verify_ssl=False,
        timeout=TIMEOUT,
    )

    data = load_data(sys.argv[1])

    metrics = create_metrics(data)
    metrics = add_tags(metrics, config["instance"])

    data_string = metrics_to_string(metrics)
    lines = [line for line in data_string.splitlines() if line.strip()]

    if not lines:
        return

    try:
        influx_client.write_points(data_string)
    except (InfluxDBClientError, InfluxDBServerError) as exc:
        raise RuntimeError(f"Failed to write to InfluxDB: {exc}") from exc
