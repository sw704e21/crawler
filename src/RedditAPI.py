import praw
import requests


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


class RedditAPI:
    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'permalink', 'selftext', 'score', 'created_utc', 'num_comments', 'karma')

    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def subreddit_stream(self, subreddit):

        subreddit = initialize_reddit().subreddit(subreddit)
        reddit_url = "https://www.reddit.com"
        # Loop over submissions for a given reddit
        for submission in subreddit.stream.submissions(skip_existing=True):
            # self.submissions.add(submission)

            # Adding the specified submission fields to the json object
            to_dict = vars(submission)
            redditor = to_dict['author']
            sub_dict = {field: to_dict[field] for field in self.fields}
            sub_dict['karma'] = redditor.link_karma
            sub_dict['created_utc'] *= 1000
            sub_dict['source'] = subreddit.display_name
            sub_dict['permalink'] = reddit_url + sub_dict['permalink']
            # posting submission data through the API
            self.post_data(sub_dict)

    def post_data(self, data):
        r = requests.post(self.api_url + "data", data=data)
        print(data)

        # Exception handling
        try:
            r.raise_for_status()
            print(r)
        except requests.exceptions.HTTPError as e:
            print(e)
