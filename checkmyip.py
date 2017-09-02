#!/usr/bin/python


#####           CheckMyIP Server             #####
#####        Written by John W Kerns         #####
#####       http://blog.packetsar.com        #####
##### https://github.com/packetsar/checkmyip #####


##### Inform version here #####
version = "v1.0.0"


import os
import sys
import time
import socket
import jinja2
import paramiko
import threading

j2log = "Connection from: {{ ip }} ({{ port }}) ({{ proto }})"
#j2send = "\n\n\nYour IP Address is {{ ip }} ({{ port }})\n\n\n\n"


j2send = """{


"comment": "##     Your IP Address is {{ ip }} ({{ port }})     ##",


"family": "{{ family }}", 
"ip": "{{ ip }}", 
"port": "{{ port }}"
}"""





class log_management:
	def __init__(self):
		self.logpath = "/etc/checkmyip/"
		self.logfile = "/etc/checkmyip/checkmyip.log"
		self._publish_methods()
		self.can_log = True
		try:
			paramiko.util.log_to_file('/etc/checkmyip/ssh.log')
		except IOError:
			self._create_log_dir()
	def _logger(self, data):
		logdata = time.strftime("%Y-%m-%d %H:%M:%S") + ":   " + data + "\n"
		if self.can_log:
			try:
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
		log = self._logger
		console = self._console
	def _create_log_dir(self):
		os.system('mkdir -p ' + self.logpath)
		self._console("Logpath (%s) created" % self.logpath)
		self.can_log = True


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
	def open(self):
		pass
	def close(self):
		pass
	def readlines(self):
		return self.data.split("\n")
	def __call__(self):
		return paramiko.RSAKey.from_private_key(self)


class ssh_server (paramiko.ServerInterface):
	def __init__(self):
		self.event = threading.Event()
	def check_channel_request(self, kind, chanid):
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
	def check_auth_none(self, username):
		return paramiko.AUTH_SUCCESSFUL
	def get_allowed_auths(self, username):
		return 'none'
	def check_channel_shell_request(self, channel):
		self.event.set()
		return True
	def check_channel_pty_request(self, channel, term, width, height,
								   pixelwidth, pixelheight, modes):
		return True


def j2format(j2tmp, valdict):
	template = jinja2.Template(j2tmp)
	return template.render(valdict)


def cleanip(addr):
	ip = addr[0]
	port = addr[1]
	family = "ipv6"
	if len(ip) > 6:  # If this IP is not a super short v6 address
		if ip[:7] == "::ffff:":  # If this is a prefixed IPv4 address
			ip = ip.replace("::ffff:", "")  # Return the cleaned IP
			family = "ipv4"
	return (ip, port, family)  # Return the uncleaned IP if not matched


def listener(port, talker):
	listen_ip = ''
	listen_port = port
	buffer_size = 100  # Normally 1024, but we want fast response
	while True:
		sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((listen_ip, listen_port))
		sock.listen(buffer_size)
		client, addr = sock.accept()
		ip, port, family = cleanip(addr)
		valdict = {"ip": ip, "port": port, "family": family}
		thread = threading.Thread(target=talker, args=(client, valdict))
		thread.start()


def telnet_talker(client, valdict):
	valdict.update({"proto": "telnet"})
	log(j2format(j2log, valdict))
	client.send(j2format(j2send, valdict))  # echo
	client.close()
	#quit()


def ssh_talker(client, valdict):
	valdict.update({"proto": "ssh"})
	t = paramiko.Transport(client, gss_kex=True)
	t.set_gss_host(socket.getfqdn(""))
	t.load_server_moduli()
	t.add_server_key(rsa_key()())
	server = ssh_server()
	t.start_server(server=server)
	chan = t.accept(20)
	if chan:
		server.event.wait(10)
		#chan.send(j2format(j2log, valdict))
		log(j2format(j2log, valdict))
		chan.send('%s' % j2format(j2send, valdict))
		chan.makefile('rU').readline().strip('\r\n')
	chan.close()
	#quit()


def http_talker(client, valdict):
	def recv_all(sock):
		prev_timeout = sock.gettimeout()
		try:
			sock.settimeout(0.01)
			rdata = []
			while True:
				try:
					rdata.append(sock.recv(MAX_PACKET))
				except socket.timeout:
					return ''.join(rdata)
		finally:
			sock.settimeout(prev_timeout)
	def normalize_line_endings(s):
		return ''.join((line + '\n') for line in s.splitlines())
	while True:
		# headers and body are divided with \n\n (or \r\n\r\n - that's why we
		# normalize endings). In real application usage, you should handle 
		# all variations of line endings not to screw request body
		request = normalize_line_endings(recv_all(client)) # hack again
		request_head, request_body = request.split('\n\n', 1)
		# first line is request headline, and others are headers
		request_head = request_head.splitlines()
		request_headline = request_head[0]
		# headers have their name up to first ': '. In real world uses, they
		# could duplicate, and dict drops duplicates by default, so
		# be aware of this.
		request_headers = dict(x.split(': ', 1) for x in request_head[1:])
		# headline has form of "POST /can/i/haz/requests HTTP/1.0"
		request_method, request_uri, request_proto = request_headline.split(' ', 3)
		response_body = [
			'<html><body><h1>Hello, world!</h1>',
			'<p>This page is in location %(request_uri)r, was requested ' % locals(),
			'using %(request_method)r, and with %(request_proto)r.</p>' % locals(),
			'<p>Request body is %(request_body)r</p>' % locals(),
			'<p>Actual set of headers received:</p>',
			'<ul>',
		]
		for request_header_name, request_header_value in request_headers.iteritems():
			response_body.append('<li><b>%r</b> == %r</li>' % (request_header_name, \
				request_header_value))
		response_body.append('</ul></body></html>')
		response_body_raw = ''.join(response_body)
		# Clearly state that connection will be closed after this response,
		# and specify length of response body
		response_headers = {
				'Content-Type': 'text/html; encoding=utf8',
				'Content-Length': len(response_body_raw),
				'Connection': 'close',
		}
		response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
																						response_headers.iteritems())
		# Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
		response_proto = 'HTTP/1.1'
		response_status = '200'
		response_status_text = 'OK' # this can be random
		# sending all this stuff
		client.send('%s %s %s' % (response_proto, response_status, \
																										response_status_text))
		client.send(response_headers_raw)
		client.send('\n') # to separate headers from body
		client.send(response_body_raw)
		# and closing connection, as we stated before
		client.close()


def start():
	talkers = {22: ssh_talker, 23: telnet_talker, 80: telnet_talker}
	for talker in talkers:
		thread = threading.Thread(target=listener, args=(talker, talkers[talker]))
		thread.daemon = True
		thread.start()
	while True:
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			quit()


class CheckMyIP_Client:
	def __init__(self):
		self._json = __import__('json')  # Import the JSON library
		self._socket = __import__('socket')  # Import the socket library
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
		self._data = sock.recv(1024)  # Recieve data from the buffer
		sock.close()  # Close the socket
		return self._json.loads(self._data)  # Return the JSON data
	def set_family(self, family):  # Method to set the IP address family
		allowed = ["auto", "ipv4", "ipv6"]  # Allowed input values
		if family in allowed:
			self._af = family
		else:
			raise Exception("Allowed families are 'auto', 'ipv4', 'ipv6'")


if __name__ == "__main__":
	logging = log_management()
	start()