import sys
import socket
import jinja2
import paramiko
import threading

j2log = "Connection from: {{ ip }} ({{ port }})"
j2send = "\n\n\nYour IP Address is {{ ip }} ({{ port }})\n\n\n\n"


paramiko.util.log_to_file('demo_server.log')


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


def cleanip(ip):
    if len(ip) > 6:  # If this IP is not a super short v6 address
        if ip[:7] == "::ffff:":  # If this is a prefixed IPv4 address
            return ip.replace("::ffff:", "")  # Return the cleaned IP
    return ip  # Return the uncleaned IP if not matched


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
        thread = threading.Thread(target=talker, args=(client, addr))
        thread.start()


def telnet_talker(client, addr):
    valdict = {"ip": cleanip(addr[0]), "port": addr[1]}
    print(j2format(j2log, valdict))
    client.send(j2format(j2send, valdict))  # echo
    client.close()


def ssh_talker(client, addr):
    t = paramiko.Transport(client, gss_kex=True)
    t.set_gss_host(socket.getfqdn(""))
    t.load_server_moduli()
    t.add_server_key(rsa_key()())
    server = ssh_server()
    t.start_server(server=server)
    chan = t.accept(20)
    server.event.wait(10)
    valdict = {"ip": cleanip(addr[0]), "port": addr[1]}
    #chan.send(j2format(j2log, valdict))
    chan.send('%s' % j2format(j2send, valdict))
    chan.makefile('rU').readline().strip('\r\n')
    chan.close()


def start():
    talkers = {2200: ssh_talker, 23: telnet_talker}
    for talker in talkers:
        thread = threading.Thread(target=listener, args=(talker, talkers[talker]))
        thread.daemon = False
        thread.start()

if __name__ == "__main__":
    start()



