#!/bin/bash

##################################
# run.sh
##################################

# Find the directory this script is being run from

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $SCRIPT_DIR/run_dev.sh >>/dev/null 2>/var/log/acp_prod/deconz2acp.err & disown

