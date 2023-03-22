GPU Benchmarking Script
=======================

This script is used to benchmark the GPU performance of a machine. It is
based on the SciML Benchmarking suite, which can be found here:
https://github.com/stfc-sciml/sciml-bench . (Our thanks to the SciML team).

The script is designed to be run on a machine with a GPU, and will
run with the specified number of GPUs (default 1).

THe underlying benchmarking tool is PyTorch. The script will install
PyTorch and the SciML Benchmarking suite and required drivers automatically.

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
