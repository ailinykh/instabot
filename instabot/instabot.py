#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import pickle
import random
import sys

from datetime import datetime
from functools import wraps
from typing import Callable

from instaloader import Profile, ProfileNotExistsException

from .__init__ import __version__
from .persistence import Follower, Persistence
from .instaloader import Instaloader

class Instabot:
    
    def __init__(self, config=None, **kwargs):
        self.logger = logging.getLogger(__package__)
        self.config = config

        now_time = datetime.now()
        log_string = 'Instabot v%s started at %s' % (
            __version__, now_time.strftime('%d.%m.%Y %H:%M')
        )
        self.logger.info(log_string)

    def collect(self):
        usernames = self.config.get('profiles')

        instaloader = Instaloader()
        db = Persistence('sqlite:///db.sqlite3')

        for username in usernames:
            self.logger.info('Processing username {}'.format(username))
            
            for post in instaloader.get_last_user_posts(username):
                self.logger.info('Post {} has {} comments'.format(post.shortcode, post.comments))    
                
                media = db.get_media(post)

                if not media or media.comments * 1.5 < post.comments:
                    self.logger.info('Processing comments from {}'.format(post.shortcode))
                    
                    for comment in post.get_comments():
                        db.create_follower(comment.owner)

                        for answer in comment.answers:
                            db.create_follower(answer.owner)

                    db.create_or_update_media(post)
                    # return
                else:
                    self.logger.info('Skipping post {}'.format(post.shortcode))
        #     n = 0
        #     break  

    def job(self): # workflow
        instaloader = Instaloader()
        instaloader.login(
            self.config.get('login'),
            self.config.get('password')
            )
        db = Persistence('sqlite:///db.sqlite3')
        
        def get_valid_profile(candidate: Follower) -> Profile:
            try:
                profile = instaloader.get_profile(candidate.username)
            except ProfileNotExistsException:
                self.logger.warning(f'Profile {candidate.username} not found.')
                db.update(candidate, filtered='user not found')
                return None

            # check already follower
            if profile.follows_viewer:
                self.logger.warning(f'{profile.username} already a follower')
                db.update(candidate, filtered='already follower')
                return None

            # check already followed
            if profile.followed_by_viewer:
                self.logger.warning(f'{profile.username} already followed')
                db.update(candidate, filtered='already followed')
                return None
            
            return profile

        
        # check limits
        likes_available = 60 - len(db.get_resent_likes())
        follows_available = 60 - (len(db.get_resent_followees()) + len(db.get_resent_unfollowees()))

        self.logger.info(f'Available: likes {likes_available}, follows {follows_available}')

        if likes_available > 0:
            candidate = db.get_candidate_to_like()
            profile = get_valid_profile(candidate)

            if profile is not None:
                for post in profile.get_posts():
                    j, ok = instaloader.like_post(post)
                    if ok:
                        self.logger.info(f'Successfully liked post {post.shortcode} by {profile.username}')
                        db.update(candidate, last_liked=datetime.now())
                    else:
                        self.logger.warning(f'Bad status {j}')
                    break

        if follows_available > 0:
            candidate = db.get_candidate_to_follow()
            profile = get_valid_profile(candidate)

            if profile is not None:
                j, ok = instaloader.follow_user(profile)
                if ok:
                    self.logger.info(f'Successfully followed {profile.username}')
                    db.update(candidate, last_followed=datetime.now())
                else:
                    self.logger.warning(f'Bad status {j}')

            #TODO check who follows back


    def session(self, jsn: str, filename: str):
        if jsn is None or filename is None:
            exit('usage: python {} session session_json session_file'.format(sys.argv[0]))
        
        session = json.loads(jsn)
        with open(filename, 'wb') as sessionfile:
            os.chmod(filename, 0o600)
            pickle.dump(session, sessionfile)

    def print_session(self, filename: str):
        with open(filename, 'rb') as sessionfile:
            print(json.dumps(pickle.load(sessionfile)))

    def test(self, **kwargs):
        # instaloader = Instaloader()
        # db = Persistence('sqlite:///db.sqlite3')
        # candidate = db.get_candidate_to_follow()

        # profile = instaloader.get_profile(candidate.username)
        # db.update(candidate, some='value', oter=123, filtered='ololo it works!')
        self.logger.info('It works!')
        self.logger.warning('Warning!')