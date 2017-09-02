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






