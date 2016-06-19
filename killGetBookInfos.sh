#!/bin/bash

app_pid=`pgrep -f book.py`

if [ $app_pid ] ; then
	echo "kill process. [${app_pid}]"
	kill -9 ${app_pid}
else
	echo "already killed process."
fi
