#!/bin/bash

#########################################
# run_dev.sh
# Used to start deconz2mqtt in 'dev' mode
#########################################

# Find the directory this script is being run from

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR

pid=$(pgrep -f "python3 deconz2mqtt.py")

if [ $? -eq 0 ]
then
    echo $(date '+%s') $SCRIPT_DIR/run_dev.sh FAIL: deconz2mqtt.py already running as PID $pid
    exit 1
else
    source venv/bin/activate
    python3 deconz2mqtt.py
    exit 0
fi
