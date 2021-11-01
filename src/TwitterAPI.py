import json
import tweepy


class IDPrinter(tweepy.Stream):

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, redditAPI=""):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.redditAPI = redditAPI

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
        self.redditAPI.post_data(submission_data)

    def on_error(self, status):
        print(status)
