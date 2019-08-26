#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser

from .instabot import Instabot
from .config import logger

def main():
    parser = ArgumentParser(description='Instabot')

    choices = [func for func in dir(Instabot) if callable(getattr(Instabot, func)) and not func.startswith('_')]
    parser.add_argument('action', metavar='|'.join(choices), choices=choices)

    args = parser.parse_args()

    instabot = Instabot()

    getattr(instabot, args.action)()