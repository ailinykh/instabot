#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys

# sys.path.append(os.path.abspath('../python-telegram-handler'))

import logging.config
import telegram_handler
from config42 import ConfigManager

config = ConfigManager(path='./config.yml', prefix=__package__)

logging.config.dictConfig(config.get("logging"))