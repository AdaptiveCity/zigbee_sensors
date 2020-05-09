#!/bin/bash

##################################
# run.sh
##################################

# Find the directory this script is being run from

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR

pid=$(pgrep -f "python3 deconz2acp.py")

if [ $? -eq 0 ]
then
    echo $(date '+%s') $SCRIPT_DIR/run_dev.sh FAIL: deconz2acp.py already running as PID $pid >>/var/log/acp_prod/deconz2acp.err
    exit 1
else
    source venv/bin/activate
    nohup python3 deconz2acp.py >>/dev/null 2>>/var/log/acp_prod/deconz2acp.err & disown
    exit 0
fi

