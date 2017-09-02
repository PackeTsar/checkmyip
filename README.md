# CheckMyIP
A Telnet and SSH based IP Lookup Service








## Install Process

Change Linux SSH Port to TCP222 and reboot
```
sudo sed -i --follow-symlinks 's/#Port 22/Port 222/g' /etc/ssh/sshd_config

shutdown -r now
```

Install Dependencies
```
yum install gcc -y
yum install libffi-devel -y
yum install openssl-devel -y
pip install python-gssapi
```

Install Binary
```
cp checkmyip.py /bin/checkmyip
chmod 777 /bin/checkmyip

mkdir -p /etc/checkmyip/
```

Create Service (`vi /etc/init.d/checkmyip`)
```
#!/bin/bash
# radiuid daemon
# chkconfig: 345 20 80
# description: RADIUS to Palo-Alto User-ID Engine
# processname: radiuid

DAEMON_PATH="/bin/"

DAEMON=radiuid
DAEMONOPTS="run"

NAME=RadiUID
DESC="RADIUS to Palo-Alto User-ID Engine"
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

case "$1" in
start)
				printf "%-50s" "Starting $NAME..."
				cd $DAEMON_PATH
				PID=`$DAEMON $DAEMONOPTS > /dev/null 2>&1 & echo $!`
				#echo "Saving PID" $PID " to " $PIDFILE
				if [ -z $PID ]; then
						printf "%s
" "Fail"
				else
						echo $PID > $PIDFILE
						printf "%s
" "Ok"
				fi
;;
status)
				if [ -f $PIDFILE ]; then
						PID=`cat $PIDFILE`
						if [ -z "`ps axf | grep ${PID} | grep -v grep`" ]; then
								printf "%s
" "Process dead but pidfile exists"
						else
								echo "$DAEMON (pid $PID) is running..."
						fi
				else
						printf "%s
" "$DAEMON is stopped"
				fi
;;
stop)
				printf "%-50s" "Stopping $NAME"
						PID=`cat $PIDFILE`
						cd $DAEMON_PATH
				if [ -f $PIDFILE ]; then
						kill -HUP $PID
						printf "%s
" "Ok"
						rm -f $PIDFILE
				else
						printf "%s
" "pidfile not found"
				fi
;;

restart)
				$0 stop
				$0 start
;;

*)
				echo "Usage: $0 {status|start|stop|restart}"
				exit 1
esac
```



