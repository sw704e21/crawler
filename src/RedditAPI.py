import praw
import json
import requests
import tweepy
from src.TwitterAPI import IDPrinter

TWITTER_APP_KEY = "VVHRzSdTp6T35a04AJuqlr3SR"
TWITTER_APP_SECRET = "83MFy2JuE3sbyLhqWtpKV7KoBLQ7EDQgFCWEXVQgNqf44cJaxD"
TWITTER_KEY = "611585498-MgduwddC5tSVylz6CzUTMJKULy8qM6PJsdASvTtX"
TWITTER_SECRET = "S7gX7cTaqfnfkenpG0C3PD0Fu0YGAMKEijgGsWmsE1OZV"


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


def initialize_twitter():
    printer = IDPrinter(
        TWITTER_APP_KEY, TWITTER_APP_SECRET,
        TWITTER_KEY, TWITTER_SECRET
    )
    return printer


class RedditAPI:
    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'url', 'selftext', 'score', 'created_utc', 'num_comments')

    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.fields
        self.api_url = ""
        self.printer = initialize_twitter()

    def subreddit_stream(self, subreddit):

        subreddit = initialize_reddit().subreddit(subreddit)
        # Loop over submissions for a given reddit
        for submission in subreddit.stream.submissions():
            self.submissions.add(submission)

            # Adding the specified submission fields to the json object
            to_dict = vars(submission)
            sub_dict = {field: to_dict[field] for field in self.fields}

            # posting submission data through the API
            submission_data = json.dump(sub_dict)
            self.post_data(submission_data)

    def twitter_stream(self, keywords, languages):

        # Starting the actual stream
        self.printer.filter.track = keywords
        self.printer.filter.languages = languages
        try:
            self.printer.sample()
        except self.printer.on_request_error as e:
            print(e)
        except self.printer.on_disconnect as e:
            print(e)

    def post_data(self, data):
        r = requests.post(self.api_url + "data/reddit", data=data)

        # Exception handling
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)


redditAPI = RedditAPI()
redditAPI.printer.redditAPI = redditAPI
redditAPI.twitter_stream(["BTC", "Bitcoin"], ['English'])
