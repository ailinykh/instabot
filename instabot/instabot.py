#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time

from datetime import datetime

from instaloader import Profile, ProfileNotExistsException, TooManyRequestsException

from .__init__ import __version__
from .persistence import Follower, Persistence
from .instaloader import Instaloader


class Instabot:

    def __init__(self, config=None, **kwargs):
        self.logger = logging.getLogger(__package__)
        self.config = config

        self.instaloader = Instaloader()
        self.logger.debug(f"Using database {self.config.get('database')}")
        self.db = Persistence(self.config.get('database'))

        now_time = datetime.now()
        log_string = f"Instabot v{__version__} started at {now_time.strftime('%d.%m.%Y %H:%M')}"
        self.logger.info(log_string)

    def collect(self):
        last_block = self.db.get_current_soft_block()

        if last_block is not None:
            timeout = (last_block.checked - last_block.blocked).total_seconds() * 0.5 if last_block.checked else 0  # noqa: E501
            self.logger.info(f'Currently in soft block. Wating {timeout} seconds...')
            time.sleep(timeout)

        try:
            self._collect()
            if last_block is not None:
                self.db.update(last_block, unblocked=datetime.now())
            return
        except TooManyRequestsException:
            self.logger.info(f'Soft block. Too many requests')
        except ProfileNotExistsException:
            self.logger.info(f'Soft block. Profile not exists')

        # Soft block occured :(
        if last_block is not None:
            self.db.update(last_block, checked=datetime.now())
        else:
            self.db.create_soft_block()

    def _collect(self):
        config = self.config.get('collect')

        if not config['profiles']:
            self.logger.error('profiles are empty')
            return

        if not config['limit']:
            self.logger.error('profiles limit not set')
            return

        for profile in config['profiles']:
            self.logger.info(f'Processing profile {profile}')

            posts = self.instaloader.get_last_user_posts(profile)

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

                        if len(self.db.get_last_updated_followers()) > config['limit']:
                            self.logger.info('Profiles time limit reached. Exiting...')
                            return

                    self.db.create_or_update_media(post)
                else:
                    self.logger.info(f'Skipping post {post.shortcode}')

    def job(self):  # workflow
        self.instaloader.login(
            self.config.get('login'),
            self.config.get('password')
            )

        def get_valid_profile(candidate: Follower) -> Profile:
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
            profile = get_valid_profile(candidate)

            if profile is not None:
                for post in profile.get_posts():
                    j, ok = self.instaloader.like_post(post)
                    if ok:
                        self.logger.info(
                            f'Successfully liked post {post.shortcode} by {profile.username}')
                        self.db.update(candidate, last_liked=datetime.now())
                    else:
                        self.logger.warning(f'Bad status {j}')
                    break

        if follows_available > 0:
            candidate = self.db.get_candidate_to_follow()
            profile = get_valid_profile(candidate)

            if profile is not None:
                j, ok = self.instaloader.follow_user(profile)
                if ok:
                    self.logger.info(f'Successfully followed {profile.username}')
                    self.db.update(candidate, last_followed=datetime.now())
                else:
                    self.logger.warning(f'Bad status {j}')

            # TODO check who follows back

    def test(self, **kwargs):
        profile = self.config.get('profiles')[0]
        self.logger.info(f'Checking {profile}')

        try:
            posts = self.instaloader.get_last_user_posts(profile)
        except ProfileNotExistsException:
            self.logger.info(f'Profile not exists')
            return

        self.logger.warning('Got profile posts {posts}!')
        return posts
