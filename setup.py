#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    required = [l.strip("\n") for l in f if l.strip("\n") and not l.startswith("#")]


def find_version():
    with open(path.join(path.dirname(__file__), 'instabot/__init__.py')) as f:
        for line in f:
            m = re.match("__version__ = '(.*)'", line)
            if m:
                return m.group(1)
    raise SystemExit("Could not find version string.")


setup(
    name="instabot",
    packages=find_packages(),
    version=find_version(),
    python_requires=">3.7.0",
    license="MIT",
    description="Instagram Bot",
    # long_description="",
    # long_description_content_type="text/markdown",
    author="Anthony Ilinykh",
    author_email="anthonyilinykh@gmail.com",
    url="https://github.com/ailinykh/instabot",
    download_url="https://github.com/ailinykh/instabot/tarball/master",
    keywords="instagram bot",
    install_requires=required,
    entry_points={"console_scripts": ["instabot = instabot.__main__:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
