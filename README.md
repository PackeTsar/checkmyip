# CheckMyIP (TelnetMyIP  [![Twitter][twitter-logo]][twitter]) [![CheckMyIP][logo]][twitter]
A Telnet and SSH Based Public IP Address Lookup Service

Lookup your IP Address from a CLI with `telnet telnetmyip.com` or `ssh sshmyip.com`


-----------------------------------------
###   VERSION   ###
The version of CheckMyIP documented here is: **v1.0.0**

-----------------------------------------
###   TABLE OF CONTENTS   ###
1. [What is CheckMyIP](#what-is-checkmyip)
2. [How to Use](#how-to-use)
3. [Using the API](#using-the-api)
4. [Install Process](#install-process)
5. [Contributing](#contributing)


-----------------------------------------
###   WHAT IS CHECKMYIP   ###
Everybody has used a service like [WhatIsMyIP.com](https://www.whatismyip.com/) before. If you are an IT engineer or even an amateur technology enthusiast, then you have probably had a reason to check to see your public IP address. This service works great when a browser is available, but at times it is not. We often find ourselves logged into a remote Linux machine or a network switch/router which has a command line and terminal clients (Telnet and SSH), but no browser. The CheckMyIP app and the **TelnetMyIP.com** and **SSHMyIP.com** public services were created with this in mind.


-----------------------------------------
###   HOW TO USE   ###
Using the public **TelnetMyIP.com** and **SSHMyIP.com** services is pretty easy: simply connect to them with a terminal client. You can use a telnet client with TCP port 23 (`telnet telnetmyip.com`), or a SSH client with TCP port 22 (`ssh sshmyip.com`). The SSH connection requires no authentication, but your SSH client may require you to enter a username, you can use anything you want as it gets ignored anyways(`ssh -limrootbitch telnetmyip.com`).

You can also browse to the HTTP version of the service at [TelnetMyIP.com](http://telnetmyip.com/) which will return a JSON reply with your IP information.

To enable the use of this service as a simple API, the response is formatted as a JSON document. See the [Using the API](#using-the-api) section for information on how to leverage the API.

**Note:** _You can also connect to_ `ipv4.telnetmyip.com` _or_ `ipv6.telnetmyip.com` _if you want to check a specific IP stack._

**Note:** _The DNS records for_ `telnetmyip.com` _and_ `sshmyip.com` _point to the same services._


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
###   INSTALL PROCESS   ###
If you would rather set up your own private instance of CheckMyIP, then you can follow the below instructions to set it up for yourself.

Change Linux SSH Port to TCP 222 and reboot
```
sudo sed -i --follow-symlinks 's/#Port 22/Port 222/g' /etc/ssh/sshd_config

shutdown -r now
```

Install Dependencies
```
yum install git -y
yum install gcc -y
yum install libffi-devel -y
yum install openssl-devel -y
pip install python-gssapi
```

Clone Repo
```
git clone https://github.com/PackeTsar/checkmyip.git
```

Install Binary
```
cd checkmyip

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
STDOUTFILE=/etc/checkmyip/stdout.log
STDERR=/etc/checkmyip/stderr.log

NAME=CheckMyIP
DESC="CheckMyIP Daemon"
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

case "$1" in
start)
				printf "%-50s" "Starting $NAME..."
				cd $DAEMON_PATH
				PID=`stdbuf -o0 $DAEMON >> $STDOUTFILE 2>>$STDERR & echo $!`
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
###   CONTRIBUTING   ###
If you would like to help out by contributing code or reporting issues, please do!

Visit the GitHub page (https://github.com/packetsar/checkmyip) and either report an issue or fork the project, commit some changes, and submit a pull request.

[twitter-logo]: http://www.packetsar.com/wp-content/uploads/twitter-logo-35.png
[twitter]: https://twitter.com/TelnetMyIP
[logo]: http://www.packetsar.com/wp-content/uploads/checkmyip_icon-100.gif
[whatismyip]: https://www.whatismyip.com/
