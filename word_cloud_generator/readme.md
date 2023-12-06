# Word Cloud Generator

## General Info

This is a Python script that when run, creates a filter word cloud from the summary of tickets over a time period.

The script takes ~10 seconds to complete on a month of tickets

Unit tests exist which test the logic of the methods the script uses, and the tests should be run whenever changes are made to the code.

## Requirements

requests: 2.31.0
parameterized: 0.9.0
python-dateutil: 2.8.2
wordcloud: 1.9.2

## Setup
Running the script:
```
$ cd ../word_cloud_generator
$ pip install -r requirements.txt
$ python3 word_cloud_generator.py
```

Running the unit tests:
```
$ python3 -m unittest discover -s ./test -p "test_*.py"
```