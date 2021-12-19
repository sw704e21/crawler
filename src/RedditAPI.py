import praw
import requests
import logging
import time
logger = logging.getLogger("crawler")


def initialize_reddit():
    reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
    return reddit


class RedditAPI:
    # Specify the wanted fields from praw.submissions to be send through the API
    fields = ('title', 'permalink', 'selftext', 'score', 'created_utc', 'num_comments', 'id')

    def __init__(self):
        self.headline = set()
        self.submissions = set()
        self.list_of_items = []
        self.seen_submissions = set()
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def subreddit_stream(self, tags):

        reddit_url = "https://www.reddit.com"
        reddit = initialize_reddit()
        while True:
            try:
                for submission in reddit.subreddit("all").stream.submissions():
                    # Adding the specified submission fields to the json object
                    redditor = submission.author
                    sub_dict = {'karma': redditor.link_karma + redditor.comment_karma,
                                'created_utc': submission.created_utc * 1000,
                                'permalink': reddit_url + submission.permalink,
                                'uuid': submission.id,
                                'source': 'reddit',
                                'title': submission.title,
                                'selftext': submission.selftext,
                                'score': submission.score,
                                'num_comments': submission.num_comments}
                    # sub_dict['source'] = subreddit.display_name
                    # posting submission data through the API
                    self.post_data(sub_dict)
            except Exception as e:
                logger.error(e)

    def post_data(self, data):
        logger.info(f"Post sub {data['permalink']}")
        r = requests.post(self.api_url + "data", data=data)

        # Exception handling
        try:
            r.raise_for_status()
            logger.info(r)
        except requests.exceptions.HTTPError as e:
            logger.error(e.args)
        finally:
            return r.status_code
