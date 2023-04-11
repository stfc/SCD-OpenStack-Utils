GPU Benchmarking Script
=======================

This script is used to benchmark the GPU performance of a machine. It is
based on the Phoronix Test Suite and will run a number of benchmarks automatically.

The script is designed to be run on a machine with a GPU, and will
run with the specified number of GPUs (default 1).

Requirements
------------

- Rocky Linux 8.x Machine
- GPU with CUDA support  (Note: We have selected Phoronix Test Suite as we can switch to OpenCL in the future)
- Internet access

Scripts
-------

- gpu_benchmark.sh - Script to run the benchmark. This benchmarks card #0 by default using the Phoronix Test Suite and will output a file gpu-benchmark.txt in the current directory.
- power_perf.sh - Script to capture power data from IPMI whilst running hashcat on preset known easy passwords. It requires a physical host for ipmitool to work. It will output a file power.log in the current directory every minute.

Usage
-----
sudo ./gpu_benchmark.sh [-n <number of test iterations>]
sudo ./power_perf.sh

cat gpu-benchmark.txt
cat power.log

Benchmark Description
---------------------

The benchmarks run are:

- fahbench https://openbenchmarking.org/test/pts/fahbench

- realsr-ncnn https://openbenchmarking.org/test/pts/realsr-ncnn

- octanebench https://openbenchmarking.org/test/pts/octanebench

These represent a variety of workloads, with tests that place substantial load on the higher class compute GPUs.

Scoring
-------

Separately to this tool, we normalise the scores to ensure they use a similar scoring scale to fahbench and octanebench, as follows:

realsr-ncnn (TAA: N): 1000 / seconds
realsr-ncnn (TAA: Y): 10000 / seconds

These FAH and Octane benchmark scores are then combined to give a final score for each GPU.
