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
- GPU with CUDA support  (Note: We have selected PyTorch for the ability to run OpenCL in the future)
- Internet access
- 64GB+ of RAM. (Where the RAM Disk takes 40GB).

Usage
-----
sudo ./gpu_benchmark.sh [-n <number of GPUs>]

Results will be stored in ~/results as *.txt files, where the number corresponds to the number of GPUs used.
Log files from the training runs are stored in ~/results/*.logs files.
