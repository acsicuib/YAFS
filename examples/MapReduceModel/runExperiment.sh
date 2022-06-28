#!/bin/bash


# This scripts runs the phases of the experiment (generation of scenario, simulation, analysis and graphs generation) in a local server

# A trap function of error commands.
# It uses telegram-send library to notify the progress

set -eE
trap 'printerr' ERR
function printerr(){
 local lc="$BASH_COMMAND" rc=$? ln=${BASH_LINENO[$i]}
 echo "$(date +%s) : Command [ ${$lc} ] error"
 telegram-send "Command [ $lc ] error"
}


# Update paths according with your configuration

# Invocation example:
# + The code is the name of the project folder (acronym from centrality, userlocation, wei...
# + The step arg. avoid the initial steps. So, if step == 3, it avoids 1 and 2 "run" commands.
#./runExperiment.sh --step all --duration 100000 --simulations 1 --code edpt0 --centrality eigenvector --userlocation dispersed --edgeweight propagation --topology twolevel



export PYTHONPATH=$PYTHONPATH:/home/uib/src/YAFS/src/:src/examples/MapReduceModel/

WORK_DIR_BASE=/home/uib/src/YAFS/allocationConfigurable
WORK_DIR=/home/uib/src/YAFS/allocationConfigurable
WD=/home/uib/src/YAFS/src/examples/MapReduceModel/


#Default values
SIMULATIONS=1
TIME=100000


STEP=all
COUNTERSTEP=1
CODE=etpd
CENTRALITY=""
USERLOCATION=""
EDGEWEIGHT=""
TOPOLOGY=""
CLOUDLOCATION=""







# Parse command line arguments

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
    --step)
      STEP=$2
      shift
      ;;
    --code)
      CODE=$2
      shift
      ;;
    --centrality)
      CENTRALITY=$2
      shift
      ;;
    --userlocation)
      USERLOCATION=$2
      shift
      ;;
    --edgeweight)
      EDGEWEIGHT=$2
      shift
      ;;
    --topology)
      TOPOLOGY=$2
      shift
      ;;
    --cloudlocation)
      CLOUDLOCATION=$2
      shift
      ;;
    *)
      echo "error: unrecognized argument $1"
      exit 1
      ;;
  esac
  shift
done


#Defining results path
#firstletter=${word:0:1}
echo $CODE

WORK_DIR=${WORK_DIR_BASE}/experiment_${CODE}/data/
echo ${WORK_DIR_BASE}/experiment_${CODE}/data/

#Defining the number of experiment
#oldnum=`cut -d ',' -f2 file1.txt`
#newnum=`expr $oldnum + 1`
#sed -i "s/$oldnum\$/$newnum/g" file1.txt



# Wrapper function to print the command being run
function run {
  echo $STEP

  if [ "$STEP" = "all" ]; then
    echo $COUNTERSTEP
    echo "$ $@"
    telegram-send $2
    "$@"
  elif (( COUNTERSTEP >= STEP)); then
    echo $COUNTERSTEP
    echo "$ $@"
    telegram-send $2
    "$@"
  else
    echo "Avoiding execution"
    echo "$ $@"
  fi

  COUNTERSTEP=$((COUNTERSTEP+1))
}

# STEP 1 - Generation JSON Structures
echo '>> Generating JSON data'
run python ${WORK_DIR_BASE}/testingCentralities.py \
   --work-dir $WORK_DIR_BASE \
   --code-exp $CODE \
   --centrality $CENTRALITY \
   --userlocation $USERLOCATION \
   --edgeweight $EDGEWEIGHT \
   --topology $TOPOLOGY \
   --cloudlocation $CLOUDLOCATION
echo ''

# # STEP 2 - Generation JSON Structures
# echo '>> MOVING JSON data'
# run mv ${WORK_DIR}jsonmodel\*.json ${WORK_DIR}
# echo ''

# 2 Extract the data files
echo '>> Launching Simulation'
run python ${WD}main.py  \
   --work-dir ${WORK_DIR} \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

# 3Preprocess the datasets
echo '>> Analysing results N50'
run python ${WD}analyse_results_n50.py  \
   --work-dir $WORK_DIR \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

echo '>> 4 Analysing results F100'
run python ${WD}analyse_results_f100.py  \
   --work-dir $WORK_DIR \
   --duration $TIME \
   --simulations $SIMULATIONS
echo ''

#step 5
echo '>> Moving (by default --filter csv)'
run python /home/uib/src/toDropbox.py  \
    --work-dir $WORK_DIR \
    --code $CODE

#step 6
run python /home/uib/src/toDropboxCarlos.py  \
    --work-dir $WORK_DIR \
    --code $CODE 
echo ''

#step 7
echo '>> 5 Generating  graphs F100'
run python ${WD}graficas_resultados_f100.py  \
   --work-dir $WORK_DIR \
   --simulations $SIMULATIONS
echo ''


#step 8
echo '>> Generating  graphs N50'
run python ${WD}graficas_resultados_n50.py  \
   --work-dir $WORK_DIR \
   --simulations $SIMULATIONS
echo ''

#ste 9
echo '>> Generating  graphs availability'
run python ${WD}grafica_availability.py  \
   --work-dir $WORK_DIR \
echo ''


#step 10
echo '>> Moving (by default all.pdf files)'
run python /home/uib/src/toDropbox.py  \
    --work-dir $WORK_DIR \
    --code $CODE \
    --filter '*.pdf'
echo ''

#step 11
run python /home/uib/src/toDropboxCarlos.py  \
    --work-dir $WORK_DIR \
    --code $CODE \
    --filter '*.pdf'
echo ''
#step 12
run python /home/uib/src/toDropbox.py  \
    --work-dir $WORK_DIR \
    --code $CODE \
    --filter 'aceleracion*'
echo ''
#step 13
run python /home/uib/src/toDropboxCarlos.py  \
    --work-dir $WORK_DIR \
    --code $CODE \
    --filter 'aceleracion*'
echo ''





echo '>> Sending the last telegram'
telegram-send "The end"
echo ''


