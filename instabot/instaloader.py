# -*- coding: utf-8 -*-

from __future__ import print_function
from functools import wraps
from typing import Callable, Dict

import logging
import os
import requests

from instaloader import InstaloaderContext
from instaloader import Post
from instaloader import Profile
from instaloader import LoginRequiredException, TwoFactorAuthRequiredException


SCAM_FILTER = [
    'SMM',
    'выезд',
    'выплат',
    'гарантия',
    'деньги',
    'дeньги',  # latin letters
    'оставка',
    'дeeньги',
    'доход',
    'заказ',
    'запись на',
    'зараб',
    'зapaб',  # latin letters
    'зарбот',
    # 'зож', # regexp needed
    'инвестиции',
    'крипто',
    'коммерч',
    'личка переполнена',
    'мнe пишeт',  # latin letters
    'т акции',
    'oпpoc',  # latin letters
    'ОТВЕТ ТУТ',
    'получаю от',
    'предоплата',
    'продам',
    'продаю',
    'продвижение',
    'раскрутка',
    'скидк',
]

AUDIENCE_FILTER = [
    ' ПП',
    'без сахара',
    'врач',
    'комплексный подход',
    'консульт',
    'копирайт',
    'косметолог',
    'коуч',
    'нутрициолог',
    'оптом',
    'питание',
    'под ключ',
    'подписывайтесь',
    'помощник',
    'правильн',
    'марафон',
    'менеджер',
    'разбогатеть',
    'ручная работа',
    'ручной работы',
    'риэлтор',
    'СММ',
    'твой личный',
    'только по в',
    'требуются',
    'тренер',
]


def _filtered(self) -> str:
    if self.followers == 0:
        return 'fake'
    if self.followees == 0 or self.followers / self.followees > 2 \
            and self.followers > 1000:
        return 'selebgram'
    if self.followees > 1000:
        return 'massfollower'
    if any(ext in self.biography for ext in SCAM_FILTER):
        return 'fraud'
    if any(ext in self.biography for ext in AUDIENCE_FILTER):
        return 'non-target'
    return None


Profile.filtered = property(_filtered)


def copy_session(session: requests.Session) -> requests.Session:
    """Duplicates a requests.Session."""
    new = requests.Session()
    new.cookies = requests.utils.cookiejar_from_dict(
        requests.utils.dict_from_cookiejar(session.cookies))
    new.headers = session.headers.copy()  # type: ignore
    return new


def _requires_login(func: Callable) -> Callable:
    """Decorator to raise an exception if herewith-decorated
        function is called without being logged in"""
    @wraps(func)
    def call(instaloader, *args, **kwargs):
        if not instaloader.c.is_logged_in:
            raise LoginRequiredException("Login required.")
        return func(instaloader, *args, **kwargs)
    return call


class Instaloader:
    """
    Instaloader

    """

    url = 'https://www.instagram.com/'
    url_like = 'https://www.instagram.com/web/likes/%s/like/'
    url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'
    url_comment = 'https://www.instagram.com/web/comments/%s/add/'
    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'
    url_media = 'https://www.instagram.com/p/%s/'
    url_user_detail = 'https://www.instagram.com/%s/'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(__package__)

        self.s = requests.Session()
        self.c = InstaloaderContext()

    def login(self, username, password):
        filename = 'session-' + username.lower()
        try:
            with open(filename, 'rb') as sessionfile:
                self.c.load_session_from_file(username, sessionfile)
                self.logger.info(f'Loaded session from {filename}.')
        except FileNotFoundError as err:
            self.logger.debug(err)
            self.logger.warning('Session file does not exist yet - Logging in.')
        if not self.c.is_logged_in or username != self.c.test_login():
            try:
                self.c.login(username, password)
            except TwoFactorAuthRequiredException:
                self.logger.warning('2FA required!')
            with open(filename, 'wb') as sessionfile:
                os.chmod(filename, 0o600)
                self.c.save_session_to_file(sessionfile)
                self.logger.info(f'Saved session to {filename}.')
        self.logger.info(f'Logged in as {username}.')

    def get_profile(self, username: str) -> Profile:
        return Profile.from_username(self.c, username)

    def get_post(self, shortcode: str) -> Post:
        return Post.from_shortcode(self.c, shortcode)

    def get_last_user_posts(self, username: str, count: int = 10) -> [Post]:
        self.logger.debug(f'Getting last posts for {username}')
        profile = Profile(self.c, {'username': username})
        return [x for _, x in zip(range(count), profile.get_posts())]

    @_requires_login
    def follow_user(self, profile: Profile) -> (Dict, bool):
        assert not profile.followed_by_viewer, 'You must unfollow to follow'
        self.c.do_sleep()
        with copy_session(self.c._session) as tmpsession:
            tmpsession.headers['referer'] = self.url_user_detail % profile.username
            res = tmpsession.post(self.url_follow % profile.userid)
            return res.json(), res.status_code == 200

    @_requires_login
    def unfollow_user(self, profile: Profile) -> (Dict, bool):
        assert profile.followed_by_viewer, 'You must follow to unfollow'
        self.c.do_sleep()
        with copy_session(self.c._session) as tmpsession:
            tmpsession.headers['referer'] = self.url_user_detail % profile.username
            res = tmpsession.post(self.url_unfollow % profile.userid)
            return res.json(), res.status_code == 200

    @_requires_login
    def like_post(self, post: Post) -> (Dict, bool):
        self.c.do_sleep()
        with copy_session(self.c._session) as tmpsession:
            tmpsession.headers['referer'] = self.url_media % post.shortcode
            res = tmpsession.post(self.url_like % post.mediaid)
            return res.json(), res.status_code == 200

    @_requires_login
    def unlike_post(self, post: Post) -> (Dict, bool):
        self.c.do_sleep()
        with copy_session(self.c._session) as tmpsession:
            tmpsession.headers['referer'] = self.url_media % post.shortcode
            res = tmpsession.post(self.url_unlike % post.mediaid)
            return res.json(), res.status_code == 200
