from multiprocessing import Process
from RedditAPI import RedditAPI
import TwitterAPI
import logging
import kafka
import psutil
logger = logging.getLogger("crawler")


class MultiProcessScraper:

    def __init__(self):
        # Kafka server config
        self.host = "kafka-cryptopinion.northeurope.cloudapp.azure.com"
        self.port = "9092"
        self.server = self.host + ":" + self.port
        self.topic = "CoinsToTrack"
        self.api_version = (2, 4, 0)

        self.tags = []
        self.reddit = None
        self.twitter = None

    def start_reddit(self):
        crawler = RedditAPI()
        crawler.subreddit_stream(self.tags)

    def start_twitter(self, lang=None):
        if lang is None:
            lang = ['en']
        crawler = TwitterAPI.initialize_twitter()
        crawler.twitter_stream(self.tags, languages=lang)

    def restart_process(self):
        reddit = Process(target=self.start_reddit)
        reddit.start()
        if self.reddit:
            p = psutil.Process(self.reddit)
            p.kill()
        self.reddit = reddit.pid
        # twitter = Process(target=self.start_twitter)
        # twitter.start()
        # if self.twitter:
        #     p = psutil.Process(self.twitter)
        #     p.kill()
        # self.twitter = twitter.pid

    def run(self):
        logger.info("Starting kafka consumer")
        consumer = kafka.KafkaConsumer(self.topic, bootstrap_servers=self.server, api_version=self.api_version,
                                       group_id="Crawler")
        self.restart_process()
        for m in consumer:
            try:
                tag = m.value.decode('utf-8')
                logger.info(f"Received tag: {tag}")
                self.tags.append(tag)
                self.restart_process()
            except Exception as e:
                logger.error(e.args)
