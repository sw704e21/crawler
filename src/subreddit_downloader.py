import sys
import praw
import typer

# noinspection PyUnresolvedReferences
# import pretty_errors  # keep the import to have better error messages

from os.path import join
from typer import Argument
from typer import Option
from typing import Optional
from loguru import logger
from codetiming import Timer
from pushshift_py import PushshiftAPI
from prawcore.exceptions import NotFound

from update_posts import UpdatePosts
import logging
import datetime
import os
flogger = logging.getLogger("downloader")
flogger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s:%(levelname)s - %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

now = datetime.datetime.now()

handler = logging.FileHandler(f"{os.getcwd()}/logs/{now.day}-{now.month}-{now.year}.log", "a")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
flogger.addHandler(handler)

class OutputManager:
    """
    Class used to collect and store data (submissions and comments)
    """
    params_filename = "params.yaml"

    def __init__(self, output_dir: str, subreddit: str):
        self.submissions_list = []
        self.submissions_raw_list = []
        self.comments_list = []
        self.comments_raw_list = []
        self.run_id = ""
        self.data = []

        self.subreddit_dir = join(output_dir, subreddit)
        self.runtime_dir = join(self.subreddit_dir, self.run_id)

        self.submissions_output = join(self.runtime_dir, "submissions")
        self.sub_raw_output = join(self.runtime_dir, "submissions", "raw")
        self.comments_output = join(self.runtime_dir, "comments")
        self.comments_raw_output = join(self.runtime_dir, "comments", "raw")
        self.params_path = join(self.runtime_dir, OutputManager.params_filename)

        self.total_submissions_counter = 0
        self.total_comments_counter = 0
        self.api_url = "http://cryptoserver.northeurope.cloudapp.azure.com/"

    def reset_lists(self):
        self.submissions_list = []
        self.submissions_raw_list = []
        self.comments_list = []
        self.comments_raw_list = []

    def store(self):
        # Track total data statistics

        if len(self.submissions_raw_list) > 0:
            return self.submissions_list


def init_locals(debug: str,
                output_dir: str,
                subreddit: str,
                utc_upper_bound: str,
                utc_lower_bound: str,
                run_args: dict,
                ) -> (str, OutputManager):
    assert not (utc_upper_bound and utc_lower_bound), "`utc_lower_bound` and " \
                                                      "`utc_upper_bound` parameters are in mutual exclusion"
    run_args.pop("reddit_secret")

    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    direction = "after" if utc_upper_bound else "before"
    output_manager = OutputManager(output_dir, subreddit)

    return direction, output_manager


def init_clients(reddit_id: str,
                 reddit_secret: str,
                 reddit_username: str
                 ) -> (PushshiftAPI, praw.Reddit):
    pushshift_api = PushshiftAPI()

    reddit_api = praw.Reddit(
        client_id=reddit_id,
        client_secret=reddit_secret,
        user_agent=f"python_script:subreddit_downloader:(by /u/{reddit_username})",
    )

    return pushshift_api, reddit_api


def utc_range_calculator(utc_received: int,
                         utc_upper_bound: int,
                         utc_lower_bound: int
                         ) -> (int, int):
    """
    Calculate the max UTC range seen.
    Increase/decrease utc_upper_bound/utc_lower_bound according with utc_received value
    """
    if not utc_upper_bound or not utc_lower_bound:
        utc_upper_bound = utc_received
        utc_lower_bound = utc_received

    utc_lower_bound = utc_lower_bound if utc_received > utc_lower_bound else utc_received
    utc_upper_bound = utc_upper_bound if utc_received < utc_upper_bound else utc_received

    return utc_lower_bound, utc_upper_bound


def comments_fetcher(sub, output_manager, reddit_api, comments_cap):
    """
    Comments fetcher
    Get all comments with depth-first approach
    Solution from https://praw.readthedocs.io/en/latest/tutorials/comments.html
    """
    try:
        submission_rich_data = reddit_api.submission(id=sub.id)
        logger.debug(f"Requesting {submission_rich_data.num_comments} comments...")
        submission_rich_data.comments.replace_more(limit=comments_cap)
        comments = submission_rich_data.comments.list()
    except NotFound:
        logger.warning(f"Submission not found in PRAW: `{sub.id}` - `{sub.title}` - `{sub.full_link}`")
        return
    for comment in comments:
        comment_useful_data = {
            "id": comment.id,
            "submission_id": sub.id,
            "body": comment.body.replace('\n', '\\n'),
            "created_utc": int(comment.created_utc),
            "parent_id": comment.parent_id,
            "permalink": comment.permalink,
        }
        output_manager.comments_raw_list.append(comment.__dict__)
        output_manager.comments_list.append(comment_useful_data)


def submission_fetcher(sub, output_manager: OutputManager):
    """
    Get and store reddit submission info
    """
    # Sometimes the submission doesn't have the selftext
    self_text_normalized = sub.selftext.replace('\n', '\\n') if hasattr(sub, "selftext") else "<not selftext available>"

    submission_useful_data = {
        "title": sub.title.replace('\n', '\\n'),
        "full_link": sub.full_link,
        "score": sub.score,
        "created_utc": sub.created_utc,
        "selftext": self_text_normalized,
        "num_comments": sub.num_comments

    }
    output_manager.submissions_list.append(submission_useful_data)
    output_manager.submissions_raw_list.append(sub.d_)


class HelpMessages:
    help_reddit_url = "https://github.com/reddit-archive/reddit/wiki/OAuth2"
    help_reddit_agent_url = "https://github.com/reddit-archive/reddit/wiki/API"
    help_praw_replace_more_url = "https://asyncpraw.readthedocs.io/en/latest/code_overview/other/co" \
                                 "mmentforest.html#asyncpraw.models.comment_forest.CommentForest.replace_more"

    subreddit = "The subreddit name"
    output_dir = "Optional output directory"
    batch_size = "Request `batch_size` submission per time"
    laps = "How many times request `batch_size` reddit submissions"
    reddit_id = f"Reddit client_id, visit {help_reddit_url}"
    reddit_secret = f"Reddit client_secret, visit {help_reddit_url}"
    reddit_username = f"Reddit username, used for build the `user_agent` string, visit {help_reddit_agent_url}"
    utc_after = "Fetch the submissions after this UTC date"
    utc_before = "Fetch the submissions before this UTC date"
    debug = "Enable debug logging"
    comments_cap = f"Some submissions have 10k> nested comments and stuck the praw API call." \
                   f"If provided, the system requires new comments `comments_cap` times to the praw API." \
                   f"`comments_cap` under the hood will be passed directly to `replace_more` function as " \
                   f"`limit` parameter. For more info see the README and visit {help_praw_replace_more_url}."


# noinspection PyTypeChecker
@Timer(name="main", text="Total downloading time: {minutes:.1f}m", logger=logger.info)
def downloader(subreddit: str = Argument(..., help=HelpMessages.subreddit),
               output_dir: str = Option("./data/", help=HelpMessages.output_dir),
               batch_size: int = Option(10, help=HelpMessages.batch_size),
               laps: int = Option(3, help=HelpMessages.laps),
               reddit_id: str = Option(..., help=HelpMessages.reddit_id),
               reddit_secret: str = Option(..., help=HelpMessages.reddit_secret),
               reddit_username: str = Option(..., help=HelpMessages.reddit_username),
               utc_after: Optional[str] = Option(None, help=HelpMessages.utc_after),
               utc_before: Optional[str] = Option(None, help=HelpMessages.utc_before),
               comments_cap: Optional[int] = Option(None, help=HelpMessages.comments_cap),
               debug: bool = Option(False, help=HelpMessages.debug),
               ):
    """
    Download all the submissions and relative comments from a subreddit.
    """

    # Init
    utc_upper_bound = utc_after
    utc_lower_bound = utc_before
    direction, out_manager = init_locals(debug,
                                         output_dir,
                                         subreddit,
                                         utc_upper_bound,
                                         utc_lower_bound,
                                         run_args=locals())
    pushshift_api, reddit_api = init_clients(reddit_id, reddit_secret, reddit_username)
    logger.info(f"Start download: "
                f"UTC range: [{utc_lower_bound}, {utc_upper_bound}], "
                f"direction: `{direction}`, "
                f"batch size: {batch_size}, "
                f"total submissions to fetch: {batch_size * laps}")

    # Start the gathering
    up = UpdatePosts()
    for lap in range(laps):
        logger.debug(f"New lap start: {lap}")
        lap_message = f"Lap {lap}/{laps} completed in ""{minutes:.1f}m | " \
                      f"[new/tot]: {len(out_manager.comments_list)}/{out_manager.total_comments_counter}"
        flogger.debug(f"Lap {lap}/{laps}")

        with Timer(text=lap_message, logger=logger.info):
            # Reset the data already stored
            out_manager.reset_lists()

            # Fetch data in the `direction` way
            submissions_generator = pushshift_api.search_submissions(subreddit=subreddit,
                                                                     limit=batch_size,
                                                                     sort='desc' if direction == "before" else 'asc',
                                                                     sort_type='created_utc',
                                                                     after=utc_upper_bound if
                                                                     direction == "after" else None,
                                                                     before=utc_lower_bound if
                                                                     direction == "before" else None,
                                                                     )

            for sub in submissions_generator:
                logger.debug(f"New submission `{sub.full_link}` - created_utc: {sub.created_utc}")

                # Fetch the submission data
                submission_fetcher(sub, out_manager)

                # Fetch the submission's comments
                comments_fetcher(sub, out_manager, reddit_api, comments_cap)

                # Calculate the UTC seen range
                utc_lower_bound, utc_upper_bound = utc_range_calculator(sub.created_utc,
                                                                        utc_upper_bound,
                                                                        utc_lower_bound)
            # Store data (submission and comments)
            up.update_data(out_manager.store())

            # Check the bounds
            assert utc_lower_bound < utc_upper_bound, f"utc_lower_bound '{utc_lower_bound}' should be " \
                                                      f"less than utc_upper_bound '{utc_upper_bound}'"
        logger.debug(f"utc_upper_bound: {utc_upper_bound} , utc_lower_bound: {utc_lower_bound}")

    logger.info(f"Stop download: lap {laps}/{laps} [total]: {out_manager.total_comments_counter}")


if __name__ == '__main__':
    typer.run(downloader)
