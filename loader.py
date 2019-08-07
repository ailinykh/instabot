#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

from instaloader import InstaloaderContext
from instaloader import Profile
from instaloader import Post

import datetime
import logging
import re

import requests

FILTER_WORDS = [
    'предоплата', 'доставка', 'заказ', 'крипто', 'инвестиции', 'заработок',
]

def __filtered(self) -> str:
    if self.followees > 1000:
        return 'massfollower'
    if self.followees == 0 or self.followers / self.followees > 2:
        return 'selebgram'
    if self.followers == 0 or self.followees / self.followers > 2:
        return 'fake'
    if any(ext in self.biography for ext in FILTER_WORDS):
        logger = logging.getLogger(self.__class__.__name__)
        logger.info('Biography filter ({}) {}'.format(self.username, self.biography))
        return 'biography'
    return None

Profile.filtered = property(__filtered)

class Instaloader:
    """
    Instaloader

    """

    url = "https://www.instagram.com/"
    url_media = "https://www.instagram.com/p/%s/"
    url_user_detail = "https://www.instagram.com/%s/"

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.s = requests.Session()
        self.c = InstaloaderContext()

        now_time = datetime.datetime.now()
        log_string = "Instaloader v0.0.1 started at %s:" % (
            now_time.strftime("%d.%m.%Y %H:%M")
        )
        self.logger.info(log_string)

    def get_profile(self, username:str) -> Profile:
        return Profile.from_username(self.c, username)

    def get_last_user_posts(self, username: str, count: int = 10) -> [Post]:
        self.logger.debug(f"Getting last posts for {username}")
        profile = Profile(self.c, {"username": username})
        return [x for _, x in zip(range(count), profile.get_posts())]
        