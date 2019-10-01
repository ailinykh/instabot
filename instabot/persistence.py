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
    last_liked = Column(DateTime)
    last_followed = Column(DateTime)
    last_unfollowed = Column(DateTime)
    followed_back = Column(DateTime)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Media(Base):
    __tablename__ = 'medias'
    shortcode = Column(String, primary_key=True)
    comments = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SoftBlock(Base):
    __tablename__ = 'soft_blocks'
    blocked = Column(DateTime, default=datetime.now, primary_key=True)
    checked = Column(DateTime)
    unblocked = Column(DateTime)
    comment = Column(String)


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
            )
        self._session.add(follower)
        self._session.commit()

    def get_follower(self, profile: Profile) -> Follower:
        return self._session.query(Follower) \
            .filter(Follower.userid == profile.userid) \
            .one_or_none()

    def create_or_update_media(self, post: Post):
        media = self.get_media(post)
        if media is not None:
            media.comments = post.comments
        else:
            media = Media(
                shortcode=post.shortcode,
                comments=post.comments,
                )
            self._session.add(media)
        self._session.commit()

    def create_soft_block(self):
        self._session.add(SoftBlock())
        self._session.commit()

    def get_current_soft_block(self) -> SoftBlock:
        return self._session.query(SoftBlock) \
            .filter(SoftBlock.unblocked.is_(None)).first()

    def get_media(self, post: Post) -> Media:
        return self._session.query(Media) \
            .filter(Media.shortcode == post.shortcode).first()

    def get_last_created_followers(self, seconds: int = 300) -> [Follower]:
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=seconds)
        return self._session.query(Follower) \
            .filter(Follower.created > cut_off_time) \
            .order_by(desc(Follower.created)) \
            .all()

    def get_recent_likes(self, seconds: int = 3600) -> [Follower]:
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=seconds)
        return self._session.query(Follower) \
            .filter(Follower.last_liked > cut_off_time) \
            .order_by(desc(Follower.last_liked)) \
            .all()

    def get_recent_followees(self, seconds: int = 3600) -> [Follower]:
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=seconds)
        return self._session.query(Follower) \
            .filter(Follower.last_followed > cut_off_time) \
            .order_by(desc(Follower.last_followed)) \
            .all()

    def get_recent_unfollowees(self, seconds: int = 3600) -> [Follower]:
        now_time = datetime.now()
        cut_off_time = now_time - timedelta(seconds=seconds)
        return self._session.query(Follower) \
            .filter(Follower.last_unfollowed > cut_off_time) \
            .all()

    def get_candidate_to_like(self) -> Follower:
        return self._session.query(Follower) \
            .filter(Follower.last_liked.is_(None)) \
            .filter(Follower.followed_back.is_(None)) \
            .filter(Follower.filtered.is_(None)) \
            .filter(Follower.is_private.is_(False)) \
            .order_by(func.random()) \
            .first()

    def get_candidate_to_follow(self) -> Follower:
        return self._session.query(Follower) \
            .filter(Follower.last_followed.is_(None)) \
            .filter(Follower.followed_back.is_(None)) \
            .filter(Follower.filtered.is_(None)) \
            .filter(Follower.is_private.is_(True)) \
            .order_by(func.random()) \
            .first()

    def update(self, b: Base, **kwargs):
        for k, v in kwargs.items():
            setattr(b, k, v) if hasattr(b, k) \
                else print(f"Instance {b} has no attribute {k}")
        self._session.commit()
