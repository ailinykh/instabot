#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from persistence import Persistence
from loader import Instaloader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def main():
    import itertools

    instaloader = Instaloader()
    db = Persistence('sqlite:///db.sqlite3')
    usernames = [
        'anikoyoga'
    ]

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
                return
            else:
                logger.info('Skipping post {}'.format(post.shortcode))
    #     n = 0
    #     break    

if __name__ == '__main__':
    main()