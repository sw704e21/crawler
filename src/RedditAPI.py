import praw


class RedditAPI:

    def __init__(self):
        self.headline = set()
        self.submissions = set()

        self.seen_submissions = set()

    def initialize_reddit(self):
        reddit = praw.Reddit(client_id='y9aowlfsW7dLZyFuyrpH-w',
                         client_secret='3PSSrFjw7RX-nG6xfyFx_IFd74PHbQ',
                         user_agent='Huften')
        return reddit

    def subreddit_stream(self, subreddit):

        subreddit = self.initialize_reddit().subreddit(subreddit)

        for submission in subreddit.stream.submissions():
            self.submissions.add(submission)

    def print_submissions(self):
        print(self.submissions)

    def print_headlines(self):
        print(self.headline)


