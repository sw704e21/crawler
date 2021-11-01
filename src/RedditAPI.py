import praw
import json
import requests


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


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

    def post_data(self, data):
        r = requests.post(self.api_url + "data/reddit", data=data)

        # Exception handling
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
