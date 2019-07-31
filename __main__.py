#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from instabot import InstaBot

def main():
    instabot = InstaBot()

    media = instabot.get_media_by_tag("B0fxygcI0MH")
    return
    user = instabot.get_user_info("anikoyoga")
    for edge in user["edge_owner_to_timeline_media"]["edges"]:
        print(edge["node"]["shortcode"])

if __name__ == '__main__':
    main()