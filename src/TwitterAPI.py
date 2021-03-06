import tweepy
import requests
import logging
from tweepy import Tweet
logger = logging.getLogger("crawler")

TWITTER_APP_KEY = "VVHRzSdTp6T35a04AJuqlr3SR"
TWITTER_APP_SECRET = "83MFy2JuE3sbyLhqWtpKV7KoBLQ7EDQgFCWEXVQgNqf44cJaxD"
TWITTER_KEY = "611585498-MgduwddC5tSVylz6CzUTMJKULy8qM6PJsdASvTtX"
TWITTER_SECRET = "S7gX7cTaqfnfkenpG0C3PD0Fu0YGAMKEijgGsWmsE1OZV"


class TwitterAPI(tweepy.Stream):

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def on_status(self, status: Tweet):
        if not status.retweeted and not status.in_reply_to_user_id and not status.text.startswith("RT "):
            # Creating the dictionary to pass to the sentiment analyzer
            sub_dict = {}

            # Creating the dict to pass onto the sentiment analyzer
            # Inserting/extracting values
            sub_dict['title'] = ""
            sub_dict['permalink'] = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
            sub_dict['selftext'] = status.text
            sub_dict['score'] = status.reply_count + status.favorite_count
            sub_dict['created_utc'] = str(status.created_at)
            sub_dict['num_comments'] = status.retweet_count
            sub_dict['karma'] = status.user.followers_count
            sub_dict['uuid'] = status.id_str
            sub_dict['source'] = 'twitter'

            # Sending the json object
            self.post_data(sub_dict)

    def on_error(self, status):
        logger.error(status)

    def twitter_stream(self, keywords, languages):
        logger.debug("Starting twitter stream")
        # Starting the actual stream
        self.filter(track=keywords, languages=['en'])
        try:
            self.sample(languages=languages)
        except self.on_request_error as e:
            logging.error(e)
        except self.on_disconnect as e:
            logging.error(e)

    def post_data(self, data):
        r = requests.post(self.api_url + "data", json=data)
        logger.info(f"Post {data['permalink']}")
        # Exception handling
        try:
            r.raise_for_status()
            logger.info(r)
        except requests.exceptions.HTTPError as e:
            logger.error(e)


def initialize_twitter():
    printer = TwitterAPI(
        TWITTER_APP_KEY, TWITTER_APP_SECRET,
        TWITTER_KEY, TWITTER_SECRET
    )
    return printer
