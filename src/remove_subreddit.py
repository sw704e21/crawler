import sys
import socket
import pickle

HOST = '127.0.0.1'
PORT = 64000

if __name__ == '__main__':
    # Command line argument should be subreddit which should no longer be tracked
    new_reddit = ['stop', sys.argv[1]]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(pickle.dumps(new_reddit))
        data = s.recv(1024)
        print(pickle.loads(data))
