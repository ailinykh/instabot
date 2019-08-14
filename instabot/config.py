#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging.config

from config42 import ConfigManager

# logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

config = ConfigManager(path='./config.yml')
