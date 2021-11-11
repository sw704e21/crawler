import sys
import socket
import pickle

HOST = '127.0.0.1'
PORT = 64000

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(pickle.dumps('terminate'))
        data = s.recv(1024)
        print(pickle.loads(data))
