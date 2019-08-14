#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from instaloader import Post, Profile

Base = declarative_base()

class Follower(Base):
    __tablename__ = 'followers'
    userid = Column(Integer, primary_key=True)
    username = Column(String)
    followers = Column(Integer, default=0)
    followees = Column(Integer, default=0)
    media = Column(Integer, default=0)
    is_private = Column(Integer, default=0)
    filtered = Column(String)
    last_followed = Column(DateTime)
    last_unfollowed = Column(DateTime)
    followed_back = Column(DateTime)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now())

class Media(Base):
    __tablename__ = 'medias'
    shortcode = Column(String, primary_key=True)
    comments = Column(Integer)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now())

class Persistence():

    def __init__(self, connection_string):
        self._engine = create_engine(connection_string, echo=False)
        Base.metadata.create_all(self._engine)

        self._Session = sessionmaker(bind=self._engine)
        self._session = self._Session()

    def create_follower(self, profile: Profile):
        if self.get_follower(profile) is not None:
            return
        follower = Follower(
            userid=profile.userid,
            username=profile.username,
            followers=profile.followers,
            followees=profile.followees,
            media=profile.mediacount,
            is_private=profile.is_private,
            filtered=profile.filtered,
            created=datetime.now(), 
            updated=datetime.now()
            )
        self._session.add(follower)
        self._session.commit()

    def get_follower(self, profile: Profile):
        return self._session.query(Follower) \
            .filter(Follower.username == profile.username) \
            .one_or_none()

    def create_or_update_media(self, post: Post):
        media = self.get_media(post)
        if media is not None:
            media.updated = datetime.now()
            media.comments = post.comments()
        else:
            media = Media(
                shortcode=post.shortcode, 
                comments=post.comments,
                created=datetime.now(),
                updated=datetime.now()
                )
            self._session.add(media)
        self._session.commit()

    def get_media(self, post: Post):
        return self._session.query(Media) \
            .filter(Media.shortcode == post.shortcode).first()

    def get_resent_followees(self, seconds: int = 86400):
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=seconds)
        return self._session.query(Follower) \
            .filter(Follower.last_followed > cut_off_time) \
            .order_by(desc(Follower.last_followed)) \
            .all()

    def get_candidate_to_follow(self):
        return self._session.query(Follower) \
            .filter(Follower.last_followed == None) \
            .filter(Follower.followed_back == None) \
            .filter(Follower.filtered == None) \
            .order_by(func.random()) \
            .first()

    def update_last_followed(self, username: str):
        follower = self._session.query(Follower).filter(Follower.username == username).first()
        follower.last_followed = datetime.now()
        self._session.commit()

    def update_comment(self, username, comment):
        follower = self._session.query(Follower).filter(Follower.username == username).first()
        follower.comment = comment
        self._session.commit()