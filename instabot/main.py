#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import os
import pickle
import random
import sys

from datetime import datetime
from functools import wraps
from typing import Callable

from instaloader import ProfileNotExistsException

from persistence import Persistence
from loader import Instaloader
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def _reports(func: Callable) -> Callable:
    """Decorator to report message about job results"""
    @wraps(func)
    def call(*args, **kwargs):
        print("before")
        func(*args, **kwargs)
        print("after")
    return call

def collect():
    usernames = [
        # 'doctor_zubareva',
        'anikoyoga',
    ]

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

def job(): # workflow
    instaloader = Instaloader()
    instaloader.login(
        config.get('login'),
        config.get('password')
        )
    db = Persistence('sqlite:///db.sqlite3')
    # check if not sibscribe limit
    recent_followees = db.get_resent_followees()
    if len(recent_followees) < 5:
        candidate = db.get_candidate_to_follow()

        try:
            profile = instaloader.get_profile(candidate.username)
        except ProfileNotExistsException:
            logger.info('Profile {} not found.'.format(candidate.username))
            db.update(candidate, filtered='user not found')
            return

        # check already follower
        if profile.follows_viewer:
            logger.info('{} already a follower'.format(profile.username))
            db.update(candidate, filtered='already follower')
            return

        # check already followed
        if profile.followed_by_viewer:
            logger.info('{} already followed'.format(profile.username))
            db.update(candidate, filtered='already followed')
            return

        # like some media
        if not profile.is_private:
            logger.info('Profile not private')
            likes_needed = random.randrange(4)
            likes_affixed = 0
            for post in profile.get_posts():
                if likes_affixed == likes_needed:
                    break
                logger.info('Like post {}'.format(post.shortcode))
                instaloader.like_post(post)
                likes_affixed += 1
                db.update(candidate, last_liked=datetime.now())

        # all ok. Trying to follow
        logger.info('Following {}...'.format(profile.username))
        j = instaloader.follow_user(profile)
        if j['status'] == 'ok':
            logger.info('Successfully followed {}'.format(profile.username))
            db.update(candidate, last_followed=datetime.now())
        else:
            logger.info('Bad status {}'.format(j))

        #TODO check who follows back
    else:
        logger.info('Daily followees limit reached')


def session(jsn: str, filename: str):
    if jsn is None or filename is None:
        exit('usage: python {} session session_json session_file'.format(sys.argv[0]))
    
    session = json.loads(jsn)
    with open(filename, 'wb') as sessionfile:
        os.chmod(filename, 0o600)
        pickle.dump(session, sessionfile)

def print_session(filename: str):
    with open(filename, 'rb') as sessionfile:
        print(json.dumps(pickle.load(sessionfile)))

@_reports
def test(*args, **kwargs):
    instaloader = Instaloader()
    db = Persistence('sqlite:///db.sqlite3')
    candidate = db.get_candidate_to_follow()

    profile = instaloader.get_profile(candidate.username)
    db.update(candidate, some='value', oter=123, filtered='ololo it works!')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        func = locals()[sys.argv[1]] if sys.argv[1] in locals() else sys.argv[1]
        if callable(func):
            print('Invoking {}()'.format(func.__name__))
            func(*sys.argv[2:])
        else:
            print('{} is not callable'.format(func))