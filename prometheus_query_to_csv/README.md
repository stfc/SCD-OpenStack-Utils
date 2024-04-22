<h2>Prometheus Query to CSV</h2>
<h4>Author: Kalibh Halford</h3>
This script collects data from Prometheus and writes it to a CSV file.<br>
- It will correctly format data from **openstack** and **node** query variables (e.g.`openstack_nova_vcpus_used`).<br>
- It uses a time range to query over a period of time. The time is required to be in UNIX Epoch format (e.g. `1710770960`).<br>
- You may need to adjust with the step (seconds) in the RawData class init as sometimes you will be querying at an interval where there is no data. This is avoidable by using a very small step. However, that can return duplicated results.<br>
- If you are querying a large amount of data, you may need to increase the amount of RAM allocated to Python. Pagination could be introduced into the script, but it's out of scope for this small use case.<br>
- The default endpoint for a Prometheus host is: `http://<host_address>:9090/api/v1/query_range`<br>
- The script will make a csv file for each query variable in the same directory as itself in the format (Date Time Hostname Value).<br>
