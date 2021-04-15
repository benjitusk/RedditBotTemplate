#!/usr/bin/python3
import os
import praw
from urlextract import URLExtract


# CONFIG START #
def load_list_from_file(filename):
    with open(filename, 'a+') as file:
        list_from_file = file.read()
        list_from_file = list_from_file.split('\n')
        list_from_file = list(filter(None, list_from_file))
        return list_from_file


reddit = praw.Reddit('link')
extractor = URLExtract()
blacklisted_usernames = load_list_from_file('blacklisted_usernames.txt')
blacklisted_threads = load_list_from_file('blacklisted_threads.txt')
blacklisted_urls = load_list_from_file('blacklisted_urls.txt')
# The computer that this bot runs on all the time in my (Benji's) house
# (I'm just gonna call this computer the server) has an
# 'environment variable' (its like a variable in python, but it's system-wide.) called 'PRODUCTION'.
# If an environment variable called 'PRODUCTION' exists and has any value (in my case it
# happens to be set to True, just cause that is a sensible variable value), then we know
# that this code is executing on the server. If this environment variable does NOT exist, then
# it means that this code is executing on our own end (NOT THE SERVER), so we should assume debugging to be TRUE
if os.getenv('PRODUCTION'):
    DEBUG = False
else:
    # However, if this code is not executing on
    # If DEBUG is True, print debug info, only scan one subreddit, and force the script to crash on Exceptions
    DEBUG = True

# To MANUALLY DISABLE DEBUG MODE UNCOMMENT THIS LINE:
# DEBUG = False

if DEBUG:
    subreddit = 'all'  # 'testingground4bots'
else:
    subreddit = 'all-testingground4bots'

# CONFIG END #


# How should we approach this? Here are three possible methods:
#
# Method A:
#   Keep an updated list of all the comments
#   in every sigle thread
#
#   Pros:
#       * Bot will be widely used
#       * Since we're tracking EVERY thread, we don't
#           have to use up our API requests checking if
#           the thread meets requirements (cuz there are no requirements)
#       * The list of URL's will be updated in realtime
#   Cons:
#       * We are tracking EVERY. SINGLE. THREAD. ON. REDDIT.
#    ===>  This alone could disqualify Method A. <===
#       * The bot would be spamming all over Reddit
#       * I probably don't have enough storage (2TB) to keep track of this
#
# Method B
#   When triggered, get a list of all URL's
#   in a thread (via PushShift) and reply with that data
#
#   Pros:
#       * Since we are only interacting with threads
#           in which we are explicitly summoned, we don't
#           have to worry about using up our API requests checking
#           if the thread meets any requirements for replying
#       * This bot will only run when triggered, so it won't spam Reddit
#   Cons:
#       * This bot will not be used very much.
#           While that isn't a problem per-se, I still see
#           it as a con.
#       * This method will not keep the list updated,
#             it will be a one time event, not a live display of links
#
#
# Method C:
#   If a processed comment matches a
#   Set of Criteria^, get a list of all
#   URL's in the thread (Via PushShift) and make
#   a comment with that data. Add the thread_id
#   to a list of threads that we are watching
#   and if a new comment containing a URL is sent
#   to that thread, find our comment and update it
#   with the new link
#
#   ^Set of Criteria:
#     * Username, thread_id, subreddit, and url domain
#         cannot be in blacklist
#     * The submission that the comment belongs
#         must be 'popular'
#         * A popular submission requires:
#             * a comment count of ___.
#             * at least ___ URL's in the comments.
#             * at least ___ minutes old
#         * The problem with these requirements is
#             that checking the above means making an API
#             request each time we check the parent post.
#             While there are ways to filter the comments
#             so that we're not requesting information on the
#             parent submission of EVERY comment sent to Reddit,
#             even with these filters, we're still _way_ past our
#             API limit of 100 req/sec (i think). We either
#             need a new set of criteria or a better preliminary_comment_check()
#
#   Pros:
#       * The list is kept live
#       * We are not tracking EVERY thread, only popular ones
#       * The bot will be fairly active without being spammy
#   Cons:
#       * In order to process the Set of Criteria, we will be
#           using up our API requests checking for the requirements.


def main():
    # Scan every single comment sent to reddit as it comes in
    for comment in reddit.subreddit(subreddit).stream.comments(pause_after=0, skip_existing=DEBUG):
        # If it fails the initial checks...
        if preliminary_comment_check(comment) == False:
            # ...skip this comment
            continue
        # If we are still processing this comment, it means
        # that at least 1 URL was found in the body of the comment.
        # The URL's in the comment were assigned to the `extracted_urls` property of the comment
        for url in comment.extracted_urls:
            # Just for debugging rn
            print(
                f'u/{comment.author.name} @ r/{comment.subreddit.display_name}:\t{url}\n')


def preliminary_comment_check(comment):
    # return False means that the preliminary check FAILED
    # return True means that the preliminary check PASSED

    # If there is no comment available when we ask for comments
    if comment == None:
        return False
    # If we blacklisted the post for some reason
    if comment.subreddit.id in blacklisted_threads:
        return False
    # If we blacklisted the user (eg. AutoModerator, our user account, certain bots, spammy users, etc)
    if comment.author.name in blacklisted_usernames:
        return False
    # Get the URL's from the comment body
    urls = extractor.find_urls(comment.body)
    # If there are no URL's found
    if urls == []:
        return False
    # Check each found URL in the comment
    for url in urls:
        # If the URL is on a blacklisted domain (perhaps adult-content websites? or maybe spam websites? idk)
        if url in blacklisted_urls:
            return False
    # Make a new property of the comment called extracted_urls
    # set this property to the list of URL('s)
    comment.extracted_urls = urls
    return True


# If this file is directly executed (as opposed to being reffered to from another file)
if __name__ == "__main__":
    # Run the main function
    main()
