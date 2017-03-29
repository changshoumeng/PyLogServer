#!/bin/bash
NOWDIR=`pwd`
rm -rf log run
mkdir log
mkdir run

nohup python $NOWDIR/echoLogSvr.py  > $NOWDIR/log/unhandle_error.log 2>&1 &

