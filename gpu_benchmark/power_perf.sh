#!/bin/bash

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
nvidia-smi || bash "$DIR/gpu_setup.sh"

sudo dnf install hashcat ipmitool -y
wget -nc https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
wget -nc https://github.com/stealthsploit/OneRuleToRuleThemStill/raw/main/OneRuleToRuleThemStill.rule

rm hashes.txt -f || true

# This was generated with the following commands
# echo -n "password" | openssl passwd -1 -stdin > hashes.txt
# echo -n "easyPassword" | openssl passwd -1 -stdin >> hashes.txt
# echo -n "myTest" | openssl passwd -1 -stdin >> hashes.txt
# echo -n "horseBattery" | openssl passwd -1 -stdin >> hashes.txt

# The dollar signs are related to the hash type, not a bash var. Disable the warning.
# shellcheck disable=SC2016
echo '$1$2by6iYgn$Cxfi5SDsfe7Z8GlfkNfyO0
$1$oeDRzC8s$xUyo21SnMLoba.JYX0qtC/
$1$/QMqw7pS$EfbzB7uf3taxeIHs1r.NM1
$1$CMp0jii5$XQubg6JNBOC9y6bxuU7NZ/
$1$IuWNtsUB$Nmub4MHpC2n2KZ0ESkg9E0' > hashes.txt

echo "Hashcat is capturing to hashcat.log"
/usr/bin/time -f %e hashcat -a 0 -m 500 hashes.txt rockyou.txt -r OneRuleToRuleThemStill.rule -O -w 3 --potfile-disable > hashcat.log 2>&1 &

rm -f power.log && nvidia-smi > power.log
i=0
while pgrep hashcat; do
  echo "Minute $i" | tee -a power.log
  ipmitool dcmi power reading | tee -a power.log
  sleep 60
done

echo "Finished capturing power"
