# -*- coding: utf-8 -*-

import logging
import random
import time

from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from instaloader import Profile, ProfileNotExistsException, TooManyRequestsException

from .__init__ import __version__
from .persistence import Follower, Persistence
from .instaloader import Instaloader

version_check = f'Python 3.6 or above required.'


def _blocking_handler(anonymously: bool = True) -> Callable:
    def actual_blocking_handler(func: Callable) -> Callable:
        """Decorator to handle blocking exceptions"""
        @wraps(func)
        def call(instabot, *args, **kwargs):
            userid = 0

            if not anonymously:
                profile = instabot.instaloader.get_profile(instabot.config.get('login'))
                userid = profile.userid

            status = instabot.db.get_current_status(userid)

            if status and not status.unblocked:
                seconds = int((status.checked - status.blocked).seconds * 0.5) if status.checked else 0  # noqa: E501
                seconds = max(seconds, 3600)  # 1 hour min
                timeout = timedelta(seconds=seconds)
                instabot.logger.info(
                    f'Currently in soft block. Timeout {timeout}...')
                instabot.logger.info(f'Next attempt in {(datetime.now() + timeout).strftime("%Y-%m-%d %H:%M:%S")}')
                time.sleep(seconds)

            try:
                rv = func(instabot, *args, **kwargs)
                if status:
                    instabot.db.update(status, unblocked=datetime.now())
                return rv
            except TooManyRequestsException:
                instabot.logger.info(f'Soft block. Too many requests')
            except ProfileNotExistsException:
                instabot.logger.info(f'Soft block. Profile not exists')

            # Soft block occured :(
            if status:
                added = len(instabot.db.get_last_created_followers())
                if added > 0:
                    instabot.logger.notify(f'New followers: {added}')
                    instabot.db.update(status, unblocked=datetime.now())
                else:
                    instabot.db.update(status, checked=datetime.now())
                    return

            instabot.db.create_status(userid=userid)
        return call
    return actual_blocking_handler


class Instabot:

    def __init__(self, config=None, **kwargs):
        self.logger = logging.getLogger(__package__)
        self.config = config

        self.instaloader = Instaloader()
        self.logger.debug(f"Using database {self.config.get('database')}")
        self.db = Persistence(self.config.get('database'))

        now_time = datetime.now()
        log_string = f"Instabot v{__version__} started at {now_time.strftime('%d.%m.%Y %H:%M')}"
        self.logger.info('==============')
        self.logger.info(log_string)

    @_blocking_handler
    def collect(self):
        config = self.config.get('collect')

        if not config['profiles']:
            self.logger.error('profiles are empty')
            return

        profiles = config['profiles']
        random.shuffle(profiles)

        for profile in profiles:
            self.logger.info(f'Processing profile {profile}')

            posts = self.instaloader.get_last_user_posts(profile)
            random.shuffle(posts)

            for post in posts:
                self.logger.info(f'Post {post.shortcode} has {post.comments} comments')

                media = self.db.get_media(post)

                if not media or media.comments * 1.5 < post.comments:
                    self.logger.info(f'Processing comments from {post.shortcode}')

                    for comment in post.get_comments():
                        if self.db.get_follower(comment.owner) is None:
                            self.db.create_follower(comment.owner)
                            self.logger.info(f'New follower added {comment.owner.username}')

                        for answer in comment.answers:
                            if self.db.get_follower(answer.owner) is None:
                                self.db.create_follower(answer.owner)
                                self.logger.info(
                                    f'New follower added {answer.owner.username} from answer')

                        if 'limit' in config:
                            last_created_followers = self.db.get_last_created_followers()
                            if len(last_created_followers) > config['limit']:
                                self.logger.info('Profiles time limit reached. Exiting...')
                                return

                    self.db.create_or_update_media(post)
                else:
                    self.logger.info(f'Skipping post {post.shortcode}')

    @_blocking_handler(anonymously=False)
    def job(self):  # workflow
        self.instaloader.login(
            self.config.get('login'),
            self.config.get('password')
            )

        def get_profile(candidate: Follower) -> Profile:
            try:
                profile = self.instaloader.get_profile(candidate.username)
            except ProfileNotExistsException:
                self.logger.warning(f'Profile {candidate.username} not found.')
                self.db.update(candidate, filtered='user not found')
                return None

            # check already follower
            if profile.follows_viewer:
                self.logger.warning(f'{profile.username} already a follower')
                self.db.update(candidate, filtered='already follower')
                return None

            # check already followed
            if profile.followed_by_viewer:
                self.logger.warning(f'{profile.username} already followed')
                self.db.update(candidate, filtered='already followed')
                return None

            return profile

        # check limits
        likes_available = 60 - len(self.db.get_recent_likes())
        follows_available = 60 - (len(self.db.get_recent_followees())
                                  + len(self.db.get_recent_unfollowees()))

        self.logger.info(f'Available: likes {likes_available}, follows {follows_available}')

        if likes_available > 0:
            candidate = self.db.get_candidate_to_like()
            profile = get_profile(candidate)

            if profile is not None:
                for post in profile.get_posts():
                    j, ok = self.instaloader.like_post(post)
                    if ok:
                        self.logger.info(
                            f'Successfully liked post {post.shortcode} by {profile.username}')
                        self.db.update(profile, last_liked=datetime.now())
                    elif j['spam']:
                        raise TooManyRequestsException
                    else:
                        self.logger.warning(f'Bad status {j}')
                    break

        if follows_available > 0:
            candidate = self.db.get_candidate_to_follow()
            profile = get_profile(candidate)

            if profile is not None:
                j, ok = self.instaloader.follow_user(profile)
                if ok:
                    self.logger.info(f'Successfully followed {profile.username}')
                    self.db.update(profile, last_followed=datetime.now())
                elif j['spam']:
                    raise TooManyRequestsException
                else:
                    self.logger.warning(f'Bad status {j}')

            # TODO check who follows back

    def test(self, **kwargs):
        profile = self.config.get('collect')['profiles'][0]
        self.logger.info(f'Checking {profile}')

        try:
            posts = self.instaloader.get_last_user_posts(profile)
        except ProfileNotExistsException:
            self.logger.info(f'Profile not exists')
            return

        self.logger.warning('Got profile posts {posts}!')
        return posts
