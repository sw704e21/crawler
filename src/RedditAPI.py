import praw
import json
import requests



class RedditAPI:


    fields = ('title', 'url', 'selftext', 'score', 'created_utc', 'num_comments')
    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.fields

    def initialize_reddit(self):
        reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
        return reddit

    def subreddit_stream(self, subreddit):

        subreddit = self.initialize_reddit().subreddit(subreddit)

        for submission in subreddit.stream.submissions():

            self.submissions.add(submission)
            to_dict = vars(submission)
            sub_dict = {field: to_dict[field] for field in self.fields}
            self.list_of_items.append(sub_dict)

            json_str = json.dumps(self.list_of_items)

            with open('data.json', 'w') as f:
                json.dump(self.list_of_items, f)


    def print_submissions(self):
        print(self.submissions)

    def print_headlines(self):
        print(self.headline)


