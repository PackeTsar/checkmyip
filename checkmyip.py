#!/usr/bin/python


#####           CheckMyIP Server             #####
#####        Written by John W Kerns         #####
#####       http://blog.packetsar.com        #####
##### https://github.com/packetsar/checkmyip #####


##### Inform version here #####
version = "v1.1.0"


##### Import python2 native modules #####
import os
import sys
import time
import socket
import jinja2
import paramiko
import threading


##### Jinja formatting for logging queries #####
j2log = "Connection from: {{ ip }} ({{ port }}) ({{ proto }})"


##### Jinja formatting for response queries #####
j2send = """{


"comment": "##     Your IP Address is {{ ip }} ({{ port }})     ##",


"family": "{{ family }}",
"ip": "{{ ip }}",
"port": "{{ port }}",
"protocol": "{{ proto }}",
"version": "%s",
"website": "https://github.com/packetsar/checkmyip"
}
""" % version


##### Handles all prnting to console and logging to the logfile #####
class log_management:
	def __init__(self):
		self.logpath = "/etc/checkmyip/"  # Log file directory path
		self.logfile = "/etc/checkmyip/%scheckmyip.log" % \
			time.strftime("%Y-%m-%d_")  # Log file full path
		self.paramikolog = "/etc/checkmyip/%sssh.log" % \
			time.strftime("%Y-%m-%d_")  # SSH log file path
		self.thread = threading.Thread(target=self._change_logfiles)
		self.thread.daemon = True
		self.thread.start()  # Start talker thread to listen to port
		self._publish_methods()  # Publish the console and log methods to glob
		self.can_log = True  # Variable used to check if we can log
		try:  # Try to configure the SSH log file, create dir if fail
			paramiko.util.log_to_file(self.paramikolog)
		except IOError:
			self._create_log_dir()
	def _logger(self, data):  # Logging method published to global as 'log'
		logdata = time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + data + "\n"
		if self.can_log:
			try:  # Try to write to log, create log dir if fail
				f = open(self.logfile, 'a')
				f.write(logdata)
				f.close()
			except IOError:
				self._console("Unable to log to logfile %s. Creating log directory" % self.logfile)
				self.can_log = False
				self._create_log_dir()
		self._console(logdata)
	def _console(self, data, timestamp=False):
		if timestamp:
			logdata = time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + data + "\n"
		else:
			logdata = data
		print(logdata)
	def _publish_methods(self):
		global log
		global console
		log = self._logger  # Global method used to write to the log file
		console = self._console  # Global method used to write to the console
	def _create_log_dir(self):  # Create the directory for logging
		os.system('mkdir -p ' + self.logpath)
		self._console("Logpath (%s) created" % self.logpath)
		self.can_log = True
	def _change_logfiles(self, thread=True):
		while True:
			time.sleep(10)
			self.logfile = "/etc/checkmyip/%scheckmyip.log" % \
				time.strftime("%Y-%m-%d_")  # Log file full path
			self.paramikolog = "/etc/checkmyip/%sssh.log" % \
				time.strftime("%Y-%m-%d_")  # SSH log file path
			paramiko.util.log_to_file(self.paramikolog)


##### Creates a RSA key for use by paramiko #####
class rsa_key:
	data = """-----BEGIN RSA PRIVATE KEY-----
	MIICWgIBAAKBgQDTj1bqB4WmayWNPB+8jVSYpZYk80Ujvj680pOTh2bORBjbIAyz
	oWGW+GUjzKxTiiPvVmxFgx5wdsFvF03v34lEVVhMpouqPAYQ15N37K/ir5XY+9m/
	d8ufMCkjeXsQkKqFbAlQcnWMCRnOoPHS3I4vi6hmnDDeeYTSRvfLbW0fhwIBIwKB
	gBIiOqZYaoqbeD9OS9z2K9KR2atlTxGxOJPXiP4ESqP3NVScWNwyZ3NXHpyrJLa0
	EbVtzsQhLn6rF+TzXnOlcipFvjsem3iYzCpuChfGQ6SovTcOjHV9z+hnpXvQ/fon
	soVRZY65wKnF7IAoUwTmJS9opqgrN6kRgCd3DASAMd1bAkEA96SBVWFt/fJBNJ9H
	tYnBKZGw0VeHOYmVYbvMSstssn8un+pQpUm9vlG/bp7Oxd/m+b9KWEh2xPfv6zqU
	avNwHwJBANqzGZa/EpzF4J8pGti7oIAPUIDGMtfIcmqNXVMckrmzQ2vTfqtkEZsA
	4rE1IERRyiJQx6EJsz21wJmGV9WJQ5kCQQDwkS0uXqVdFzgHO6S++tjmjYcxwr3g
	H0CoFYSgbddOT6miqRskOQF3DZVkJT3kyuBgU2zKygz52ukQZMqxCb1fAkASvuTv
	qfpH87Qq5kQhNKdbbwbmd2NxlNabazPijWuphGTdW0VfJdWfklyS2Kr+iqrs/5wV
	HhathJt636Eg7oIjAkA8ht3MQ+XSl9yIJIS8gVpbPxSw5OMfw0PjVE7tBdQruiSc
	nvuQES5C9BMHjF39LZiGH1iLQy7FgdHyoP+eodI7
	-----END RSA PRIVATE KEY-----
	"""
	def readlines(self):  # For use by paramiko.RSAKey.from_private_key mthd
		return self.data.split("\n")
	def __call__(self):  # Recursive method uses own object as arg when called
		return paramiko.RSAKey.from_private_key(self)


##### Imports and modifies the ServerInterface module for use by paramiko #####
class ssh_server (paramiko.ServerInterface):
	def __init__(self):
		self.event = threading.Event()
	def check_channel_request(self, kind, chanid):
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
	def check_auth_none(self, username):  # Auth none method left wide open
		return paramiko.AUTH_SUCCESSFUL
	def get_allowed_auths(self, username):  # Give no auth options
		return 'none'
	def check_channel_shell_request(self, channel):
		self.event.set()
		return True
	def check_channel_pty_request(self, channel, term, width, height,
								   pixelwidth, pixelheight, modes):
		return True


##### Method to merge Jinja templates #####
def j2format(j2tmp, valdict):
	template = jinja2.Template(j2tmp)
	return template.render(valdict).replace("\n", "\r\n")


##### Cleans IP addresses coming from socket library #####
def cleanip(addr):
	ip = addr[0]
	port = addr[1]
	family = "ipv6"
	if len(ip) > 6:  # If this IP is not a super short v6 address
		if ip[:7] == "::ffff:":  # If this is a prefixed IPv4 address
			ip = ip.replace("::ffff:", "")  # Return the cleaned IP
			family = "ipv4"
	return (ip, port, family)  # Return the uncleaned IP if not matched


##### TCP listener methods. Gets used once for each listening port #####
def listener(port, talker):
	listen_ip = ''
	listen_port = port
	buffer_size = 1024
	while True:
		sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)  # v6 family
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((listen_ip, listen_port))
		sock.listen(buffer_size)
		client, addr = sock.accept()
		ip, port, family = cleanip(addr)  # Get all cleaned IP info
		valdict = {"ip": ip, "port": port, "family": family}  # Put in dict
		thread = threading.Thread(target=talker, args=(client, valdict))
		thread.start()  # Start talker thread to listen to port


##### Telnet responder method. Is run in own thread for each telnet query #####
def telnet_talker(client, valdict, proto="telnet"):
	valdict.update({"proto": proto})  # Add the protocol to the value dict
	log(j2format(j2log, valdict))  # Log the query to the console and logfile
	client.send(j2format(j2send, valdict))  # Send the query response
	client.close()  # Close the channel


##### SSH responder method. Gets run in own thread for each SSH query #####
def ssh_talker(client, valdict, proto="ssh"):
	def makefile():  # A hack to make Cisco SSH sessions work properly
		chan.makefile('rU').readline().strip('\r\n')
	valdict.update({"proto": proto})
	log(j2format(j2log, valdict))
	t = paramiko.Transport(client, gss_kex=True)
	t.set_gss_host(socket.getfqdn(""))
	t.load_server_moduli()
	t.add_server_key(rsa_key()())  # RSA key object nested call
	server = ssh_server()
	t.start_server(server=server)
	chan = t.accept(20)
	if chan:
		server.event.wait(10)
		chan.send('%s' % j2format(j2send, valdict))  # Send the response
		thread = threading.Thread(target=makefile)
		thread.start()  # Start hack in thread since it hangs indefinately
		time.sleep(1)  # Wait a second
		chan.close()  # And kill the SSH channel
	client.close()  # And kill the session


##### HTTP responder method. Gets run in own thread for each HTTP query #####
##### Automatically detects if client is a browser or a telnet client   #####
def http_talker(client, valdict, proto="http"):
	time.sleep(.1)  # Sleep to allow the client to send some data
	client.setblocking(0)  # Set the socket recv as non-blocking
	browser = False  # Is the client using a browser?
	try:  # client.recv() will raise an error if the buffer is empty
		data = client.recv(2048)  # Recieve data from the buffer (if any)
		print(data)  # Print to stdout
		browser = True  # Set client browser to True
	except:  # If buffer was empty, then like a telnet client on TCP80
		browser = False  # Set client browser to False
	if not browser:  # If the client is not a browser
		telnet_talker(client, valdict, "http-telnet")  # Hand to telnet_talker
	else:  # If client is a browser
		# Proceed with standard HTTP response (with headers)
		valdict.update({"proto": proto})
		log(j2format(j2log, valdict))
		response_body_raw = j2format(j2send, valdict)
		response_headers_raw = """HTTP/1.1 200 OK
Content-Length: %s
Content-Type: application/json; encoding=utf8
Connection: close""" % str(len(response_body_raw))  # Response with headers
		client.send(response_headers_raw + "\n\n" + response_body_raw)
		client.close()


##### Server startup method. Starts a listener thread for each TCP port #####
def start():
	talkers = {22: ssh_talker, 23: telnet_talker, 
	80: http_talker}  # Three listeners on different ports
	for talker in talkers:
		# Launch a thread for each listener
		thread = threading.Thread(target=listener, 
			args=(talker, talkers[talker]))
		thread.daemon = True
		thread.start()
	while True:  # While loop to allow a CTRL-C interrupt when interactive
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			quit()


##### Client class to be used to make API calls to CheckMyIP server #####
class CheckMyIP_Client:
	def __init__(self):
		self._json = __import__('json')  # Import the JSON library
		self._socket = __import__('socket')  # Import the socket library
		self._raw_data = None  # Initialize the _raw_data variable
		self._data = None  # Initialize the _data variable
		self._af = "auto"  # Set the IP address family type to "auto"
		self.server = "telnetmyip.com"  # Set the default CheckMyIP server
	def get(self):  # Primary method to run IP check
		if self._af == "auto":  # If we are using an auto address family
			try:  # Try using IPv6
				sock = self._socket.socket(self._socket.AF_INET6, 
				self._socket.SOCK_STREAM)
				sock.connect((self.server, 23))
			except:  # Fall back to IPv4 if IPv6 fails
				sock = self._socket.socket(self._socket.AF_INET, 
				self._socket.SOCK_STREAM)
				sock.connect((self.server, 23))
		elif self._af == "ipv6":  # If we are using the IPv6 address family
			sock = self._socket.socket(self._socket.AF_INET6, 
			self._socket.SOCK_STREAM)
			sock.connect((self.server, 23))
		elif self._af == "ipv4":  # If we are using the IPv4 address family
			sock = self._socket.socket(self._socket.AF_INET, 
			self._socket.SOCK_STREAM)
			sock.connect((self.server, 23))
		self._raw_data = sock.recv(1024).decode()
		self._data = self._json.loads(self._raw_data)  # Recieve data from the buffer
		sock.close()  # Close the socket
		return self._data  # Return the JSON data
	def set_family(self, family):  # Method to set the IP address family
		allowed = ["auto", "ipv4", "ipv6"]  # Allowed input values
		if family in allowed:
			self._af = family
		else:
			raise Exception("Allowed families are 'auto', 'ipv4', 'ipv6'")

### CheckMyIP_Client Example Usage ###
#client = CheckMyIP_Client()
#client.get()


if __name__ == "__main__":
	logging = log_management()  # Instantiate log class
	start()  # Start the server
