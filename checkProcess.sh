#!/bin/bash

app_pid=`pgrep -f book.py`

if [ $app_pid ] ; then
	echo "working process."
else
	echo "already killed process."
fi
