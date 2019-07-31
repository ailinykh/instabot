#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import json
import logging
import re

import requests

from config import config

class InstaBot:
    """
    Instabot.py

    """

    url = "https://www.instagram.com/"
    url_tag = "https://www.instagram.com/explore/tags/%s/?__a=1"
    url_location = "https://www.instagram.com/explore/locations/%s/?__a=1"
    url_likes = "https://www.instagram.com/web/likes/%s/like/"
    url_unlike = "https://www.instagram.com/web/likes/%s/unlike/"
    url_comment = "https://www.instagram.com/web/comments/%s/add/"
    url_follow = "https://www.instagram.com/web/friendships/%s/follow/"
    url_unfollow = "https://www.instagram.com/web/friendships/%s/unfollow/"
    url_login = "https://www.instagram.com/accounts/login/ajax/"
    url_logout = "https://www.instagram.com/accounts/logout/"
    url_media_detail = "https://www.instagram.com/p/%s/?__a=1"
    url_media = "https://www.instagram.com/p/%s/"
    url_user_detail = "https://www.instagram.com/%s/"

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.s = requests.Session()
        self.c = requests.Session()

        now_time = datetime.datetime.now()
        log_string = "Instabot v0.0.1 started at %s:" % (
            now_time.strftime("%d.%m.%Y %H:%M")
        )
        self.logger.info(log_string)

    def get_user_info(self, username):
        self.logger.debug(f"Getting info {username}")
        url_tag = self.url_user_detail % (username)
        r = self.s.get(url_tag)
        if (r.text.find("The link you followed may be broken, or the page may have been removed.") != -1):
            log_string = f"Looks like account was deleted: {username}"
            self.logger.debug(log_string)
            return
        all_data = json.loads(
            re.search(
                "window._sharedData = (.*?);</script>", r.text, re.DOTALL
            ).group(1)
        )["entry_data"]["ProfilePage"][0]
        # open(f"{username}.json", 'w').write(json.dumps(all_data, indent=2))
        return all_data["graphql"]["user"]

    def get_media_by_tag(self, tag):
        self.logger.debug(f"Getting media {tag}")
        url_tag = self.url_media % (tag)
        r = self.s.get(url_tag)
        all_data = json.loads(
            re.search(
                "window._sharedData = (.*?);", r.text, re.DOTALL
            ).group(1)
        )["entry_data"]["PostPage"][0]
        open(f"{tag}.json", 'w').write(json.dumps(all_data, indent=2))
        return all_data