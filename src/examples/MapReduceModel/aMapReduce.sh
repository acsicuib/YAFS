#!/bin/bash

set -e

# export PYTHONPATH=$PYTHONPATH:/home/uib/src/YAFS/src/:src/examples/MapReduceModel/


# Parse command line arguments
WORK_DIR=/home/uib/src/YAFS/files2/
SIMULATIONS=1
TIME=100000
WD=/home/uib/src/YAFS/src/examples/MapReduceModel/
export PYTHONPATH=$PYTHONPATH:/home/uib/src/YAFS/src/:src/examples/MapReduceModel/

while [[ $# -gt 0 ]]; do
  case $1 in
    --work-dir)
      WORK_DIR=$2
      shift
      ;;
    --duration)
      TIME=$2
      shift
      ;;
    --simulations)
      SIMULATIONS=$2
      shift
      ;;
    *)
      echo "error: unrecognized argument $1"
      exit 1
      ;;
  esac
  shift
done


# Wrapper function to print the command being run
function run {
  echo "$ $@"
  telegram-send $0
  "$@"
}

# STEP 1 - Generation JSON Structures
# echo '>> Generating JSON data'
# run python ${WORK_DIR}testingCentralitieswithFogStore.py  
# echo ''

# # STEP 1 - Generation JSON Structures
# echo '>> MOVING JSON data'
# run mv ${WORK_DIR}jsonmodel\*.json ${WORK_DIR}
# echo ''

# Extract the data files
echo '>> Launching Simulation'
run python ${WD}main.py  \
   --work-dir $WORK_DIR \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

# Preprocess the datasets
echo '>> Analysing results N50'
run python ${WD}analyse_results_n50.py  \
   --work-dir $WORK_DIR \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

echo '>> Analysing results F100'
run python ${WD}analyse_results_f100.py  \
   --work-dir $WORK_DIR \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

echo '>> Moving (by default --filter csv)'
run python /home/uib/src/toDropbox.py  \
   --work-dir $WORK_DIR 
   --dst-dir '/Resultados_MapReduceModel/'
echo ''

echo '>> Sending info: Telegram'
telegram-send "Finalizado MapReduceModel"  
echo ''


