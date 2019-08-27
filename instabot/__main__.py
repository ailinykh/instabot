#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config

from argparse import ArgumentParser
from collections import OrderedDict

from config42 import ConfigManager
from config42.handlers import ArgParse

from .instabot import Instabot

schema = [
    dict(
        name="action",
        key="",
        description="Bot action",
        required=True
    ),
    dict(
        name="login",
        key="login",
        source=dict(argv=["--login"]),
        description="Your instagram username",
        required=False
    ), dict(
        name="password",
        key="password",
        source=dict(argv=["--password"]),
        description="Your instagram password",
        required=False
    ), dict(
        name="profiles",
        key="profiles",
        source=dict(argv=["--profiles"]),
        description="Profiles who collect comments from",
        type="list",
        required=False
    ), dict(
        name="SQLite3 database path",
        key="database.path",
        source=dict(argv=["--sqlite-path"]),
        description="Contains the SQLite database path",
        required=False
    ), dict(
        name="session_file",
        key="session_file",
        source=dict(argv=["--session-file"]),
        description="change the name of session file so to avoid having to login every time. Set False to disable.",
        required=False
    )
]

defaults = {'config42': OrderedDict(
    [
        ('argv', dict(handler=ArgParse, schema=schema)),
        ('env', {'prefix': 'INSTABOT'}),
        ('file', {'path': 'config.yml'}),
    ]
)}

def main():
    config = ConfigManager(schema=schema, defaults=defaults)
    config_file = config.get('config.file')
    _config = ConfigManager(schema=schema, path=config_file)
    config.set_many(_config.as_dict())
    config.commit()

    parser = ArgumentParser(description='Instabot')

    choices = [func for func in dir(Instabot) if callable(getattr(Instabot, func)) and not func.startswith('_')]
    parser.add_argument('action', metavar='|'.join(choices), choices=choices)

    args = parser.parse_args()

    print(args, config)
    instabot = Instabot(config)

    getattr(instabot, args.action)()