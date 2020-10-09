import socket
HOST = '0.0.0.1'
PORT = 8000


def connect():
    s = socket.socket()
    s.connect((HOST, PORT))


def close(s):
    s.client.close()


def send_msg(s, msg):
    s.client.send(msg)
    return s.recv(1024)