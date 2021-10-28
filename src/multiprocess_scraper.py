import csv
from multiprocessing import Process
from RedditAPI import RedditAPI


def start_crawler(reddit_name):
    crawler = RedditAPI()
    crawler.subreddit_stream(reddit_name)


class MultiProcessScraper:

    def start_scrapers(self):
        if __name__ == '__main__':
            with open('subreddits.csv', newline='') as f:
                reader = csv.reader(f)
                self.reddits_to_scrape = list(reader)
            print(self.reddits_to_scrape)
            for reddit in self.reddits_to_scrape:
                p = Process(target=start_crawler, args=(reddit),)
                p.start()
