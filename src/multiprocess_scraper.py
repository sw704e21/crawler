import csv
from multiprocessing import Process
from RedditAPI import RedditAPI


def start_crawler(reddit_name):
    crawler = RedditAPI()
    crawler.subreddit_stream(reddit_name)


class MultiProcessScraper:

    def __init__(self):
        with open('subreddits.csv', newline='') as f:
            reader = csv.reader(f)
            self.reddits_to_scrape = list(reader)

    def start_scrapers(self):
        if __name__ == '__main__':
            for reddit in self.reddits_to_scrape:
                print('Started thread')
                p = Process(target=start_crawler, args=(reddit),)
                p.start()
