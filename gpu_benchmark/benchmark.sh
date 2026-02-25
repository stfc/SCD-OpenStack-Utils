#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 United Kingdom Research and Innovation

set -e

NUM_ITERATIONS=5
print_help(){
  echo "Usage: $0 -n <number of test iterations>"
  echo "Example: $0 -n 5"
  echo "Default number of iterations is 5"
}

while getopts "n:" opt; do
  case $opt in
    n) NUM_ITERATIONS=$OPTARG ;;
    \?) print_help; exit 1 ;;
  esac
done

DIR="$(cd "$(dirname "$0")" && pwd)"
nvidia-smi || bash "$DIR/gpu_setup.sh"



echo '<?xml version="1.0"?>
<!--Phoronix Test Suite v10.8.4-->
<PhoronixTestSuite>
  <Options>
    <OpenBenchmarking>
      <AnonymousUsageReporting>FALSE</AnonymousUsageReporting>
      <IndexCacheTTL>3</IndexCacheTTL>
      <AlwaysUploadSystemLogs>FALSE</AlwaysUploadSystemLogs>
      <AllowResultUploadsToOpenBenchmarking>FALSE</AllowResultUploadsToOpenBenchmarking>
    </OpenBenchmarking>
    <General>
      <DefaultBrowser></DefaultBrowser>
      <UsePhodeviCache>TRUE</UsePhodeviCache>
      <DefaultDisplayMode>DEFAULT</DefaultDisplayMode>
      <PhoromaticServers></PhoromaticServers>
      <ColoredConsole>AUTO</ColoredConsole>
    </General>
    <Modules>
      <AutoLoadModules>toggle_screensaver, update_checker, perf_tips, ob_auto_compare, load_dynamic_result_viewer</AutoLoadModules>
    </Modules>
    <Installation>
      <RemoveDownloadFiles>FALSE</RemoveDownloadFiles>
      <SearchMediaForCache>TRUE</SearchMediaForCache>
      <SymLinkFilesFromCache>FALSE</SymLinkFilesFromCache>
      <PromptForDownloadMirror>FALSE</PromptForDownloadMirror>
      <EnvironmentDirectory>~/.phoronix-test-suite/installed-tests/</EnvironmentDirectory>
      <CacheDirectory>~/.phoronix-test-suite/download-cache/</CacheDirectory>
    </Installation>
    <Testing>
      <SaveSystemLogs>TRUE</SaveSystemLogs>
      <SaveInstallationLogs>TRUE</SaveInstallationLogs>
      <SaveTestLogs>TRUE</SaveTestLogs>
      <RemoveTestInstallOnCompletion>FALSE</RemoveTestInstallOnCompletion>
      <ResultsDirectory>~/.phoronix-test-suite/test-results/</ResultsDirectory>
      <AlwaysUploadResultsToOpenBenchmarking>FALSE</AlwaysUploadResultsToOpenBenchmarking>
      <AutoSortRunQueue>TRUE</AutoSortRunQueue>
      <ShowPostRunStatistics>TRUE</ShowPostRunStatistics>
    </Testing>
    <TestResultValidation>
      <DynamicRunCount>TRUE</DynamicRunCount>
      <LimitDynamicToTestLength>20</LimitDynamicToTestLength>
      <StandardDeviationThreshold>2.5</StandardDeviationThreshold>
      <ExportResultsTo></ExportResultsTo>
      <MinimalTestTime>2</MinimalTestTime>
      <DropNoisyResults>FALSE</DropNoisyResults>
    </TestResultValidation>
    <ResultViewer>
      <WebPort>RANDOM</WebPort>
      <LimitAccessToLocalHost>TRUE</LimitAccessToLocalHost>
      <AccessKey></AccessKey>
      <AllowSavingResultChanges>TRUE</AllowSavingResultChanges>
      <AllowDeletingResults>TRUE</AllowDeletingResults>
    </ResultViewer>
    <BatchMode>
      <SaveResults>TRUE</SaveResults>
      <OpenBrowser>FALSE</OpenBrowser>
      <UploadResults>FALSE</UploadResults>
      <PromptForTestIdentifier>FALSE</PromptForTestIdentifier>
      <PromptForTestDescription>FALSE</PromptForTestDescription>
      <PromptSaveName>TRUE</PromptSaveName>
      <RunAllTestCombinations>TRUE</RunAllTestCombinations>
      <Configured>TRUE</Configured>
    </BatchMode>
    <Networking>
      <NoInternetCommunication>FALSE</NoInternetCommunication>
      <NoNetworkCommunication>FALSE</NoNetworkCommunication>
      <Timeout>20</Timeout>
      <ProxyAddress></ProxyAddress>
      <ProxyPort></ProxyPort>
      <ProxyUser></ProxyUser>
      <ProxyPassword></ProxyPassword>
    </Networking>
    <Server>
      <RemoteAccessPort>RANDOM</RemoteAccessPort>
      <Password></Password>
      <WebSocketPort>RANDOM</WebSocketPort>
      <AdvertiseServiceZeroConf>TRUE</AdvertiseServiceZeroConf>
      <AdvertiseServiceOpenBenchmarkRelay>TRUE</AdvertiseServiceOpenBenchmarkRelay>
      <PhoromaticStorage>~/.phoronix-test-suite/phoromatic/</PhoromaticStorage>
    </Server>
  </Options>
</PhoronixTestSuite>' > /etc/phoronix-test-suite.xml
phoronix-test-suite enterprise-setup

# Phoronix options
SELECTED_TESTS="fahbench realsr-ncnn octanebench"
xvfb-run phoronix-test-suite install "$SELECTED_TESTS"


export FORCE_TIMES_TO_RUN=$NUM_ITERATIONS
export PTS_SILENT_MODE=TRUE

rm -rf /var/lib/phoronix-test-suite/test-results/

export "CUDA_VISIBLE_DEVICES=0"
echo "CUDA_VISIBLE_DEVICES set to $CUDA_VISIBLE_DEVICES"
TEST_RESULTS_IDENTIFIER="gpu-benchmark" TEST_RESULTS_NAME=gpu-benchmark \
  xvfb-run phoronix-test-suite batch-benchmark "$SELECTED_TESTS"

nvidia-smi > gpu-benchmark.txt
phoronix-test-suite result-file-to-text gpu-benchmark >> gpu-benchmark.txt
echo "Results written to gpu-benchmark.txt"
