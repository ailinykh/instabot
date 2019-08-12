#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

from persistence import Persistence
from loader import Instaloader
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def __collect_profiles(usernames):
    instaloader = Instaloader()
    db = Persistence('sqlite:///db.sqlite3')

    for username in usernames:
        logger.info('Processing username {}'.format(username))
        # profile = instaloader.get_profile(username)
        # print(profile.filtered)
        
        for post in instaloader.get_last_user_posts(username):
            logger.info('Post {} has {} comments'.format(post.shortcode, post.comments))    
            
            media = db.get_media(post)

            if not media or media.comments * 1.5 < post.comments:
                logger.info('Processing comments from {}'.format(post.shortcode))
                
                for comment in post.get_comments():
                    db.create_follower(comment.owner)

                    for answer in comment.answers:
                        db.create_follower(answer.owner)

                db.create_or_update_media(post)
                # return
            else:
                logger.info('Skipping post {}'.format(post.shortcode))
    #     n = 0
    #     break    

def test():
    instaloader = Instaloader()
    profile = instaloader.get_profile('madonna')
    print(profile._asdict())
    print(profile.filtered)

def collect():
    __collect_profiles([
        # 'doctor_zubareva'
        'anikoyoga'
    ])

def job(): # workflow
    # check if not sibscribe limit
    instaloader = Instaloader()
    instaloader.login(
        config.get('login'),
        config.get('password')
        )

if __name__ == '__main__':
    if len(sys.argv) > 1:
        func = locals()[sys.argv[1]] if sys.argv[1] in locals() else sys.argv[1]
        if callable(func):
            print('Invoking {}()'.format(func.__name__))
            func()
        else:
            print('{} is not callable'.format(func))