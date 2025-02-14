# Weekly Reporting

This script is used to upload a weekly report to an InfluxDB instance. It tags all the data points with the time when ran.<br>
If you need to back-fill data or use a different time you can do the below in the code:<br>
```
...
16 # time = datetime.datetime.now().isoformat()
17 time = "2025-01-02T15:17:37.780483"
...
```
The script uses argparse to provide an easy-to-use command line interface.<br>
There is a template yaml file [here](data.yaml) which **requires all values to be not empty**.

> **NOTE on data.yaml:**
> - Values in data.yaml must not be empty. 
> - Values which can be floating point such as Memory in TB must have .0 for whole numbers.

## Instructions:

1. Source your openstack cli venv and OpenStack admin credentials.
2. Run the `report.sh` script to generate the data file.
2. Write your token in plain text in a file e.g. "token"
3. Run `export.py` with the correct arguments, see below:

```shell
python3 export.py --host="http://172.16.103.52:8086" \
--org="cloud" \
--bucket="weekly-reports-time"
--token-file="token"
--report-file="data-9.yaml"
```
