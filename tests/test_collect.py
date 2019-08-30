from config42 import ConfigManager
from instabot import Instabot

import pytest
import requests

# @pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")

@pytest.fixture
def mock_get_posts(monkeypatch):
    def mock_get_posts(*args, **kwargs):
        print('it works')
        yield Post(None, {'shortcode': 'abcdef'})
        yield None

    monkeypatch.setattr(Profile, "get_posts", mock_get_posts)

@pytest.fixture
def mock_request_get(monkeypatch):
    def mock_get(*args, **kwargs):
        print('it works', args, kwargs)

    monkeypatch.setattr(requests.Session, 'get', mock_get)

def test_collect(tmp_path, mock_request_get):
    defaults = {
        'database': f'sqlite:///{tmp_path}/test_db.sqlite3',
        'profiles': []
    }
    config = ConfigManager(defaults=defaults)
    bot = Instabot(config)
    bot.collect()
