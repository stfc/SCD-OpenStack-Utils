# JSM Metric Collection

## General Info

This is a Python script that when run, creates 2 files: A CSV containing JSM metrics and an XLSX file generated from that CSV file.

The script takes ~10 seconds to complete

Unit tests exist which test the logic of the methods the script uses, and the tests should be run whenever changes are made to the code.

## Requirements

Script:
requests: 2.31.0
XlsxWriter: 3.1.2

Unit tests:
parameterized: 0.9.0

## Setup
Running the script:
```
$ cd ../jsm_metric_collection
$ pip install -r requirements.txt
$ python3 jsm_metric_collection.py
```

Running the unit tests:
```
$ python3 -m unittest discover -s ./test -p "test_*.py"
```