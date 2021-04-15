#!/usr/bin/python3
# ======== Imports ========
import praw  # For Reddit
import time  # For checking the inbox at a time interval
reddit = praw.Reddit('user')
print('Logged into Reddit.')

# ======== Setup Paramaters ========
# Establish who we are in terms of Reddit
me = reddit.user.me()
config = {
    "subreddit": reddit.subreddit('all'),  # Which subreddit to scan
    "inbox scan freq": 0,  # Interval of seconds to check inbox. Disables feature if <= 0
    "scan": {
        "comments": True,
        "submissions": False
    },
    "ignore automoderator": {
        "comments": True,
        "submissions": True,
        "inbox": True
    },
    "ignore distinguished": {
        "comments": False,
        "submissions": False
    },
    "ignore self": {
        "comments": True,
        "submissions": True
    },
    "ignore stickied": {
        "comments": False,
        "submissions": False
    },
}


# ======== Executed on Every Submission ========
def every_submission(submission):
    pass


# ======== Executed on Every Comment ========
def every_comment(comment):
    pass


# ======== Executed Every <inbox_scan_freq> Seconds ========
def scan_inbox():
    processed_messages = []
    for message in reddit.inbox.unread():
        processed_messages.append(message)
        if config["ignore automoderator"]["inbox"] and message.author.name == "AutoModerator":
            continue

    reddit.inbox.mark_read(processed_messages)


# ======== Boilerplate Code ========
def main():
    inbox_stopwatch = time.time()
    comment_stream = config["subreddit"].stream.comments(pause_after=-1)
    submission_stream = config["subreddit"].stream.submissions(pause_after=-1)
    while True:
        if config["scan"]["comments"] == True:
            for comment in comment_stream:
                if comment is None:
                    break
                if config["ignore automoderator"]["submissions"] and comment.author.name == "AutoModerator":
                    continue
                if config["ignore distinguished"]["comments"] and comment.distinguished:
                    continue
                if config["ignore self"]["comments"] and comment.author.name == me.name:
                    continue
                if config["ignore stickied"]["comments"] and comment.stickied:
                    continue
                every_comment(comment)
        if config["scan"]["submissions"] == True:
            for submission in submission_stream:
                if submission is None:
                    break
                if config["ignore automoderator"]["submissions"] and submission.author.name == "AutoModerator":
                    continue
                if config["ignore distinguished"]["submissions"] and submission.distinguished:
                    continue
                if config["ignore self"]["submissions"] and submission.author.name == me.name:
                    continue
                if config["ignore stickied"]["submissions"] and submission.stickied:
                    continue
                every_submission(submission)
        if config["inbox scan freq"] > 0 and time.time() - inbox_stopwatch > config["inbox scan freq"]:
            print("Scanning inbox.")
            scan_inbox()
            inbox_stopwatch = time.time()


# ======== Start the Engine ========
if __name__ == "__main__":
    main()
