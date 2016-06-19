#!/bin/sh

OUT_LOGFILE="out.log"
ERR_LOGFILE="err.log"

nohup  python book.py > $OUT_LOGFILE 2> $ERR_LOGFILE < /dev/null &
