import praw
import re
import time
import requests
import json
import pydogapi

import config


BOT_NAME = "dog_pic_bot"
SUBREDDITS = 'dogs+rarepuppers'
REPLY_TEMPLATE = '''Woof! Did I hear someone say {0}? [Here's one now!]({1})


*Bow wow wow, I'm a bot, if you don't enjoy this post PM me and I'll remove it*'''

reddit = praw.Reddit(client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET,
    user_agent=config.USER_AGENT,
    username=config.USERNAME,
    password=config.PASSWORD)

dogAPI = pydogapi.DogAPI()
breeds = dogAPI.list()['message']
# print(breeds)

removeBreeds = ['mix', 'mountain']
for toRemove in removeBreeds:
    if toRemove in breeds:
        breeds.remove(toRemove)


def reply(submission, breed):
    picUrl = dogAPI.random(breed)['message']
    replyText = REPLY_TEMPLATE.format(breed, picUrl)
    print('-----> Replying to {0} with {1}'.format(submission, replyText))
    try:
        submission.reply(replyText)
        print('<-----')
    except praw.exceptions.APIException:
        sleepTime = 300
        print('\tSleeping for %d seconds' % sleepTime)
        time.sleep(sleepTime)
        reply(submission, breed)


def processSubmission(submission):
    title = submission.title.lower()
    shouldSkipSubmission = shouldSkip(submission)

    if not shouldSkipSubmission:
        for breed in breeds:
            if breed in title:
                reply(submission, breed)
                # quit()

def shouldSkip(submission):
    title = submission.title.lower()
    if 'rip' in title:
        print('Skipping {0} because of RIP :('.format(submission))
        return True;

    postsToAvoid = ['9tin9h', '9tjtde']
    for post in postsToAvoid:
        if submission == post:
            print('Skipping because of post {0}'.format(post))
            return True


    #  if we have already posted on this submission, don't post again
    for comment in submission.comments:
        try:
            if BOT_NAME in comment.author.name:
                print('Skipping because of comment {0}'.format(comment))
                return True
        except AttributeError:
            print('Comment {0} had no author'.format(comment))

    return False



subreddit = reddit.subreddit(SUBREDDITS)
for submission in subreddit.stream.submissions():
    processSubmission(submission)
