#set -x
#set -e
PID=`cat run/master.pid`
RESULT=`ps -ef|grep $PID|grep echoLogSvr`
if [ -n "$RESULT" ];then
        echo ">> $RESULT"
	kill $PID
else
        echo "echoLogSvr is not running"
fi

echo "DONE"
