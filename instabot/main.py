#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import os
import pickle
import random
import sys

from instaloader import ProfileNotExistsException

from persistence import Persistence
from loader import Instaloader
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def _collect_profiles(usernames):
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

def collect():
    _collect_profiles([
        # 'doctor_zubareva'
        'anikoyoga'
    ])

def job(): # workflow
    instaloader = Instaloader()
    instaloader.login(
        config.get('login'),
        config.get('password')
        )
    db = Persistence('sqlite:///db.sqlite3')
    # check if not sibscribe limit
    recent_followees = db.get_resent_followees()
    if len(recent_followees) < 1:
        candidate = db.get_candidate_to_follow()

        try:
            profile = instaloader.get_profile(candidate.username)
        except ProfileNotExistsException:
            logger.info('Profile {} not found.'.format(candidate.username))
            #TODO remove from db
            return

        # check already follower
        if profile.follows_viewer:
            logger.info('{} already a follower'.format(profile.username))
            db.update_comment(profile.username, 'already follower')
            return

        # check already followed
        if profile.followed_by_viewer:
            logger.info('{} already followed'.format(profile.username))
            db.update_comment(profile.username, 'already followed')
            return

        # like some media
        likes_needed = random.randrange(4)
        likes_affixed = 0
        for post in profile.get_posts():
            if likes_affixed == likes_needed:
                break
            logger.info('Like post {}'.format(post.shortcode))
            instaloader.like_post(post)
            likes_affixed += 1

        # all ok. Trying to follow
        logger.info('Following {}...'.format(profile.username))
        j = instaloader.follow_user(profile)
        if j['status'] == 'ok':
            logger.info('Successfully followed {}'.format(profile.username))
            db.update_last_followed(profile.username)
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

def test(*args, **kwargs):
    print('test', args, kwargs)
    instaloader = Instaloader()

    try:
        profile = instaloader.get_profile('lilkus_levelap')
    except ProfileNotExistsException:
        print('LAL')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        func = locals()[sys.argv[1]] if sys.argv[1] in locals() else sys.argv[1]
        if callable(func):
            print('Invoking {}()'.format(func.__name__))
            func(*sys.argv[2:])
        else:
            print('{} is not callable'.format(func))