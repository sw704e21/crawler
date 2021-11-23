import os
import pickle
import socket
import sys
import time
from multiprocessing import Process
from RedditAPI import RedditAPI
import requests
import signal
import TwitterAPI


def start_crawler(reddit_name):
    crawler = RedditAPI()
    crawler.subreddit_stream(reddit_name)

def start_twitter_tag(tag):
    crawler = TwitterAPI().initialize_twitter()
    crawler.twitter_stream(tag)

class MultiProcessScraper:

    def __init__(self, host='127.0.0.1', port=64000):
        self.host = host
        self.port = port
        self.processes = []
        # Keep a dictionary of {tracked subreddit: processid}
        self.process_dict = {}
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"
        r = requests.get(self.api_url + "coins/all/names")
        self.reddits_to_scrape = r.json()
        r = requests.get(self.api_url + "tags/all/names")
        self.tags_to_scrape = r.json()

    def start_scrapers(self):
        for reddit in self.reddits_to_scrape:
            print('Started thread')
            p = Process(target=start_crawler, args=([reddit]))
            p.start()
            self.processes.append(p)
            self.process_dict[reddit] = p.pid
        for tag in tags_to_scrape:
            print("Started thread")
            # Creates a Process
            p = Process(target=start_twitter_tag, args=([tag], ['en']))
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
        self.start_scrapers()
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
                    if source == 'stop':
                        if data[1] in self.process_dict:
                            os.kill(self.process_dict[data[1]], signal.SIGTERM)
                            self.process_dict.pop(data[1])
                        else:
                            conn.sendall(pickle.dumps(data[1] + ' is not being tracked'))
                    if source == 'reddit':
                        new_reddit = data[1]
                        print(new_reddit)
                        p = Process(target=start_crawler, args=([new_reddit]))
                        p.start()
                        self.processes.append(p)
                        conn.sendall(pickle.dumps('Added subreddit for tracking'))
                    # A check is makde, if the data[0] specifies that this is a new twitter tag for tracking.
                    elif source == 'twittertag':
                        # If this is the case, the tag is extracted.
                        new_twitter = data[1]
                        print(new_twitter)
                        # A new process is started, starting a twitter_scraper, that listens on the tag.
                        p = Process(target=start_twitter, args=([new_twitter]))
                        p.start()
                        # The process is appended to the process list.
                        self.processes.append(p)
                        # Confirmation is sent back
                        conn.sendall(pickle.dumps('Added tag for tracking'))