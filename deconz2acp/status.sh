#!/bin/bash

PROG_NAME=deconz2acp

pid=$(pgrep -f "python3 ${PROG_NAME}.py")

if [ $? -eq 0 ]
then
  echo -e "\e[32m●\e[0m" ${PROG_NAME} running as PID $pid
  exit 0
else
  echo -e "\e[31m●\e[0m" "ERROR: ${PROG_NAME} not running?"
  exit 1
fi

