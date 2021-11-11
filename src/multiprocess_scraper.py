import csv
import pickle
import socket
import sys
import time
from multiprocessing import Process
from RedditAPI import RedditAPI


def start_crawler(reddit_name):
    crawler = RedditAPI()
    crawler.subreddit_stream(reddit_name)


class MultiProcessScraper:

    def __init__(self, host='127.0.0.1', port=64000):
        self.host = host
        self.port = port
        self.processes = []
        with open('subreddits.csv', newline='') as f:
            reader = csv.reader(f)
            self.reddits_to_scrape = list(reader)

    def start_scrapers(self):
        for reddit in self.reddits_to_scrape:
            print('Started thread')
            p = Process(target=start_crawler, args=(reddit))
            p.start()
            self.processes.append(p)

    def _recv_timeout(self, the_socket, timeout=2):
        # make socket non blocking
        the_socket.setblocking(0)

        # total data partwise in an array
        total_data = []
        data = ''

        # beginning time
        begin = time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > timeout:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time() - begin > timeout * 2:
                break

            # recv something
            try:
                data = the_socket.recv(1024 * 8)
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except socket.error:
                # Catch non-blocking socket exception as part of timeout functionality
                pass

        # join all parts to make final bytestring
        return b''.join(total_data)

    def run(self):
        #self.start_scrapers()
        print(self.reddits_to_scrape)
        print(f'Now listening on {self.host}:{self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    data = self._recv_timeout(conn)
                    print(data)
                    if not data:
                        conn.sendall(pickle.dumps('Error receiving data'))
                        break
                    if pickle.loads(bytes(data)) == 'terminate':
                        conn.sendall(pickle.dumps('Terminating server'))
                        for p in self.processes:
                            p.kill()
                        sys.exit()
                    data = pickle.loads(data)
                    source = data[0]
                    if source == 'reddit':
                        new_reddit = data[1]
                        print(new_reddit)
                        p = Process(target=start_crawler, args=([new_reddit]))
                        p.start()
                        self.processes.append(p)
                        conn.sendall(pickle.dumps('Added subreddit for tracking'))
