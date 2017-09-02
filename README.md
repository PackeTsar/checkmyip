# CheckMyIP ![CheckMyIP][logo]
A Telnet and SSH based IP Lookup Service


-----------------------------------------
###   VERSION   ###
The version of CheckMyIP documented here is: **v1.0.0**

-----------------------------------------
###   TABLE OF CONTENTS   ###
1. [What is CheckMyIP](#what-is-checkmyip)
2. [How to Use](#how-to-use)
3. [Install Process](#install-process)
4. [Using the API](#using-the-api)
5. [Contributing](#contributing)


-----------------------------------------
###   WHAT IS CHECKMYIP   ###
Everybody has used a service like [WhatIsMyIP.com](https://www.whatismyip.com/) before. If you are an IT engineer or even an amateur technology enthusiast, then you have probably had a reason to check to see your public IP address. This service works great when a browser is available, but at times it is not. We often find ourselves logged into a remote Linux machine or a network switch/router which has a command line and terminal clients (Telnet and SSH), but no browser. The CheckMyIP app and the **TelnetMyIP.com** and **SSHMyIP.com** public services were created with this in mind.


-----------------------------------------
###   HOW TO USE   ###
Using the public **TelnetMyIP.com** and **SSHMyIP.com** services is pretty easy: simply connect to them with a terminal client. You can use a telnet client with TCP port 23 (`telnet telnetmyip.com`), or a SSH client with TCP port 22 (`ssh telnetmyip.com`). The SSH connection requires no authentication, but your SSH client may require you to enter a username, you can use anything you want as it gets ignored anyways(`ssh -limrootbitch telnetmyip.com`).

To enable the use of this service as a simple API, the response to queries is formatted as a JSON document. See the [Using the API](#using-the-api) section for information on how to leverage the API.


-----------------------------------------
###   INSTALL PROCESS   ###
If you would rather set up your own private instance of CheckMyIP, then you can follow the below instructions to set it up for yourself.

Change Linux SSH Port to TCP 222 and reboot
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
# checkmyip daemon
# chkconfig: 345 20 80
# description: CheckMyIP Daemon
# processname: checkmyip

DAEMON_PATH="/bin/"

DAEMON=checkmyip
#DAEMONOPTS="run"

NAME=CheckMyIP
DESC="CheckMyIP Daemon"
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



Finish and Start Up Service
```
chmod 777 /etc/init.d/checkmyip
chkconfig checkmyip on
service checkmyip start
service checkmyip status
```


-----------------------------------------
###   USING THE API   ###
The CheckMyIP code contains the `CheckMyIP_Client` class which is an API client example which can be used to query a CheckMyIP server (like telnetmyip.com). Below is an example of how you can use it.

```
from checkmyip import CheckMyIP_Client

client = CheckMyIP_Client()
ipdict = client.get()
print("\nMy IP is %s\n" % ipdict["ip"])
print("\nI used port number %s\n" % ipdict["port"])
```

-----------------------------------------
###   CONTRIBUTING   ###
If you would like to help out by contributing code or reporting issues, please do!

Visit the GitHub page (https://github.com/packetsar/checkmyip) and either report an issue or fork the project, commit some changes, and submit a pull request.

[logo]: http://www.packetsar.com/wp-content/uploads/checkmyip_icon-100.gif
[whatismyip]: https://www.whatismyip.com/
