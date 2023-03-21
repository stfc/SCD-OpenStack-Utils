#!/bin/bash

GIT_SHA=7253289f01d4eb4daadc709267121486d9bdfb1c

set -e

NUM_GPU=1

print_usage() {
  printf "Usage: [-n]"
  printf "  -n  Number of GPUs to use (default: 1)\n"
}

while getopts 'n:v' flag; do
  case "${flag}" in
    n) NUM_GPU="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

# # Nvidia drivers - centos8
echo 'blacklist nouveau
options nouveau modeset=0' > /usr/lib/modprobe.d/blacklist-nouveau.conf
sudo dracut --force
(lsmod | grep -wq nouveau && echo "Rebooting to disable nouveau" && sudo reboot) || true

sudo dnf install tar bzip2 make automake gcc gcc-c++ pciutils elfutils-libelf-devel libglvnd-devel -y
sudo dnf install -y "kernel-devel-$(uname -r) kernel-headers-$(uname -r)" -y
wget -nc https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
nvidia-smi || sudo sh cuda_12.1.0_530.30.02_linux.run --silent
nvidia-smi || (echo "Rebooting machine to load Nvidia Driver" && sudo reboot)

# Mamba initial setup if not present
eval "$(~/mambaforge/bin/conda shell.bash hook)" || true
mamba --version || (wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && chmod +x Mambaforge-Linux-x86_64.sh && bash ./Mambaforge-Linux-x86_64.sh -b )
eval "$(~/mambaforge/bin/conda shell.bash hook)"
conda init bash

# # Env validation

mamba create --name bench python=3.9 -y
conda activate bench
mamba install -c conda-forge cudatoolkit=11.2.2 cudnn=8.1.0 -y
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
python3 -m pip install tensorflow
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Install Benchmark suite
dnf install git -y
if [ ! -d "sciml-bench" ] ; then
    git clone https://github.com/stfc-sciml/sciml-bench 
fi

cd sciml-bench
git reset --h $GIT_SHA
pip install pip --upgrade
pip install . 
sciml-bench --version

# Downgrade torch to compatible version
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
pip install pytorch-lightning==1.9.4
dnf install time -y

# Download data for benchmarks
sciml-bench download stemdl_ds1

echo "Prepping data ramdisk"
dnf install rsync -y
RAMFS=/mnt/ramfs
mkdir -p $RAMFS
mount -t tmpfs -o size=40G tmpfs $RAMFS
rsync -a ~/sciml_bench/ $RAMFS

RESULTS_DIR=~/results/
mkdir -p $RESULTS_DIR
sciml-bench install stemdl_classification

echo "SYNC: letting any outstanding disk IO settle"
sync

echo "Benchmarking with $NUM_GPU GPUs..."
sleep 3  # Give users a chance to check their GPU count

/usr/bin/time -f "%e" -p -o "$RESULTS_DIR/stemdl-$NUM_GPU.txt" sciml-bench run stemdl_classification --dataset_dir "$RAMFS/datasets/stemdl_ds1/" --mode training -b epochs 32 -b batchsize 32 -b nodes 1 -b gpus "$NUM_GPU" 2>&1 | tee "$RESULTS_DIR/stemdl-$NUM_GPU.log"
