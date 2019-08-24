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

from instaloader import Profile, ProfileNotExistsException

from .persistence import Follower, Persistence
from .instaloader import Instaloader
from .config import config

logger = logging.getLogger(__package__)

def _reports(func: Callable) -> Callable:
    """Decorator to report message about job results"""
    @wraps(func)
    def call(*args, **kwargs):
        print("before")
        func(*args, **kwargs)
        print("after")
    return call

def collect():
    usernames = config.get('profiles')

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
    
    def get_valid_profile(candidate: Follower) -> Profile:
        try:
            profile = instaloader.get_profile(candidate.username)
        except ProfileNotExistsException:
            logger.warning(f'Profile {candidate.username} not found.')
            db.update(candidate, filtered='user not found')
            return None

        # check already follower
        if profile.follows_viewer:
            logger.warning(f'{profile.username} already a follower')
            db.update(candidate, filtered='already follower')
            return None

        # check already followed
        if profile.followed_by_viewer:
            logger.warning(f'{profile.username} already followed')
            db.update(candidate, filtered='already followed')
            return None
        
        return profile

    
    # check limits
    likes_available = 60 - len(db.get_resent_likes())
    follows_available = 60 - (len(db.get_resent_followees()) + len(db.get_resent_unfollowees()))

    logger.info(f'Available: likes {likes_available}, follows {follows_available}')

    if likes_available > 0:
        candidate = db.get_candidate_to_like()
        profile = get_valid_profile(candidate)

        if profile is not None:
            for post in profile.get_posts():
                j, ok = instaloader.like_post(post)
                if ok:
                    logger.info(f'Successfully liked post {post.shortcode} by {profile.username}')
                    db.update(candidate, last_liked=datetime.now())
                else:
                    logger.info(f'Bad status {j}')
                break

    if follows_available > 0:
        candidate = db.get_candidate_to_follow()
        profile = get_valid_profile(candidate)

        if profile is not None:
            j, ok = instaloader.follow_user(profile)
            if ok:
                logger.info(f'Successfully followed {profile.username}')
                db.update(candidate, last_followed=datetime.now())
            else:
                logger.info(f'Bad status {j}')

        #TODO check who follows back


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
    # instaloader = Instaloader()
    # db = Persistence('sqlite:///db.sqlite3')
    # candidate = db.get_candidate_to_follow()

    # profile = instaloader.get_profile(candidate.username)
    # db.update(candidate, some='value', oter=123, filtered='ololo it works!')
    logger.info('It works!')
    logger.warning('Warning!')

def main():
    locls = {k: v for k, v in globals().items() if type(v).__name__ == 'function'}
    if len(sys.argv) > 1:
        func = locls[sys.argv[1]] if sys.argv[1] in locls else sys.argv[1]
        if callable(func):
            print('Invoking {}()'.format(func.__name__))
            func(*sys.argv[2:])
        else:
            print('{} is not callable'.format(func))