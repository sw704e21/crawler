import json
import tweepy
import requests

TWITTER_APP_KEY = "VVHRzSdTp6T35a04AJuqlr3SR"
TWITTER_APP_SECRET = "83MFy2JuE3sbyLhqWtpKV7KoBLQ7EDQgFCWEXVQgNqf44cJaxD"
TWITTER_KEY = "611585498-MgduwddC5tSVylz6CzUTMJKULy8qM6PJsdASvTtX"
TWITTER_SECRET = "S7gX7cTaqfnfkenpG0C3PD0Fu0YGAMKEijgGsWmsE1OZV"


class TwitterAPI(tweepy.Stream):

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, api_url=""):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.api_url = api_url

    def on_status(self, status):
        # Transforms the Status object to a json object.
        json_str = json.dumps(status._json)

        # Converts the json Object to a Dict
        aDict = json.loads(json_str)

        # Creating the dictionary to pass to the sentiment analyzer
        sub_dict = {}

        # Creating the dict to pass onto the sentiment analyzer
        user = aDict['user']

        # Inserting/extracting values
        sub_dict['title'] = ""
        sub_dict['url'] = user['url']
        sub_dict['selftext'] = aDict['text']
        sub_dict['score'] = user['followers_count'] + aDict['favorite_count']
        sub_dict['created_utc'] = aDict['created_at']
        sub_dict['num_comments'] = aDict['retweet_count']

        # Converting into a json object
        submission_data = json.dumps(sub_dict)

        # Sending the json object
        self.post_data(submission_data)

    def on_error(self, status):
        print(status)

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


def initialize_twitter(url):
    printer = IDPrinter(
        TWITTER_APP_KEY, TWITTER_APP_SECRET,
        TWITTER_KEY, TWITTER_SECRET, url
    )
    return printer
