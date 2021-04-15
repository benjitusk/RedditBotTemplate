#!/usr/bin/python3
import praw
reddit = praw.Reddit('link')
subreddit = 'all'


def main():
    # Scan every single comment sent to reddit as it comes in
    for comment in reddit.subreddit(subreddit).stream.comments(pause_after=0):
        pass


# If this file is directly executed (as opposed to being reffered to from another file)
if __name__ == "__main__":
    # Run the main function
    main()
