#!/bin/bash


# Invocation example:
# + The code is the name of the project folder (acronym from centrality, userlocation, wei...
#./aMapReduce.sh --step all --duration 100000 --simulations 1 --code edpt0 --centrality eigenvector --userlocation dispersed --edgeweight propagation --topology twolevel


# Parse command line arguments
WORK_DIR_BASE=/home/uib/src/YAFS/allocationConfigurable
WORK_DIR=/home/uib/src/YAFS/allocationConfigurable
SIMULATIONS=1
TIME=100000
WD=/home/uib/src/YAFS/src/examples/MapReduceModel/
STEP=all
COUNTERSTEP=1
CODE=etpd
export PYTHONPATH=$PYTHONPATH:/home/uib/src/YAFS/src/:src/examples/MapReduceModel/


set -eE 
trap 'printerr' ERR
function printerr(){
 local lc="$BASH_COMMAND" rc=$? ln=${BASH_LINENO[$i]}
 echo "$(date +%s) : Command [ ${$lc} ] error"
 telegram-send "Command [ $lc ] error"
}



# set -o errtrace
# trap 'printerr' errtrace
# function printerr(){
#   telegram-send "Error en configuracion: $(CODE)"  
# }

# export PYTHONPATH=$PYTHONPATH:/home/uib/src/YAFS/src/:src/examples/MapReduceModel/

CENTRALITY=""
USERLOCATION=""
EDGEWEIGHT=""
TOPOLOGY=""

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
   --topology $TOPOLOGY 

echo ''

# # STEP 1 - Generation JSON Structures
# echo '>> MOVING JSON data'
# run mv ${WORK_DIR}jsonmodel\*.json ${WORK_DIR}
# echo ''

# Extract the data files
echo '>> Launching Simulation'
run python ${WD}main.py  \
   --work-dir ${WORK_DIR} \
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

echo '>> Generating  graphs F100'
run python ${WD}graficas_resultados_f100.py  \
   --work-dir $WORK_DIR \
echo ''

echo '>> Generating  graphs N50'
run python ${WD}graficas_resultados_n50.py  \
   --work-dir $WORK_DIR \
echo ''

echo '>> Generating  graphs availability'
run python ${WD}grafica_availability.py  \
   --work-dir $WORK_DIR \
echo ''

# echo '>> Moving (by default --filter csv)'
# run python /home/uib/src/toDropbox.py  \
#    --work-dir $WORK_DIR 
# echo ''

# echo '>> Moving availability (by default --filter csv)'
# run python /home/uib/src/toDropbox.py  \
#    --work-dir $WORK_DIRjsonmodel
# echo ''

echo '>> Sending info: Telegram'
telegram-send "Finalizado MapReduceModel"  
echo ''


