# instabot

[![Actions Status](https://github.com/ailinykh/instabot/workflows/build/badge.svg)](https://github.com/ailinykh/instabot/actions)
[![codecov](https://codecov.io/gh/ailinykh/instabot/branch/master/graph/badge.svg)](https://codecov.io/gh/ailinykh/instabot)
[![Maintainability](https://api.codeclimate.com/v1/badges/dc42ab1ed9378d03bc4f/maintainability)](https://codeclimate.com/github/ailinykh/instabot/maintainability)
[![Donate](https://img.shields.io/badge/PayPal-Donate-blue.svg)](https://www.paypal.me/anthonyilinykh/10)

Yet anoter instagram bot

## Features

- Iterate over specified profiles
- Collect users who leave the comments
- Filter scum and fraud profiles
- Follow/Like users
- Respects instagram limits

#### Known instagram limits

|   | Authorized | Not authorized |
| --- | :---: | :---: |
| Follow/Unfollow  | 60/hour  | - |
| Like/Unlike  | 60/hour  | - |
| Web API requests | ? | 200/hour |

## Installation
Make sure you have __python 3.6__ or above installed

```bash
python3 --version
# Python 3.7.4
```

go to [releases](https://github.com/ailinykh/instabot/releases) section and copy link to latest __zip__ file

```bash
pip3 install https://github.com/ailinykh/instabot/archive/v<latest>.zip
```

## Configuration
instabot can read configuration settings from command line arguments

```
instabot collect --profiles people,to,collect,followers,from
```

or from `config.yml` file

```yaml
database: sqlite:///db.sqlite3
profiles:
  - people
  - to collect
  - followers
  - from
```

all available fields can be foud in [config.default.yaml](https://github.com/ailinykh/instabot/blob/master/config.default.yml)

## Running

To retreive accounts from comments and save it to database run

```
instabot collect
```

to like/follow people just write

```
instabot job
```

work in progress

## Inspired by

- [instabot.py](https://github.com/instabot-py/instabot.py)
- [instaloader](https://github.com/instaloader/instaloader)
