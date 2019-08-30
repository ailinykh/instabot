import json
import os
import pytest
import requests

from config42 import ConfigManager
from instabot import Instabot

# @pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")

# @pytest.fixture
# def mock_get_posts(monkeypatch):
#     def mock_get_posts(*args, **kwargs):
#         print('it works')
#         yield Post(None, {'shortcode': 'abcdef'})
#         yield None

#     monkeypatch.setattr(Profile, "get_posts", mock_get_posts)

@pytest.fixture
def mock_request_get(monkeypatch):
    def mock_get(session, url, **kwargs):
        parts = url.split('/')
        print(parts, url, kwargs)
        if parts[3] == 'p':
            filename = f'post_{parts[4]}.html'
        elif parts[3] == 'graphql':
            d = json.loads(kwargs["params"]["variables"])
            filename = f'graphql_{d["shortcode"]}.html'
        else:
            filename = f'username_{parts[3]}.html'
        path = os.path.join(os.path.dirname(__file__), 'data', filename)
        try:
            html = open(path, 'rb').read()
            resp = requests.Response()
            resp.status_code = 200
            resp._content = html
        except FileNotFoundError:
            resp = _get(session, url, **kwargs)
            open(path, 'w').write(resp.text)
        
        return resp

    _get = requests.Session.get
    monkeypatch.setattr(requests.Session, 'get', mock_get)

def test_collect(tmp_path, mock_request_get):
    defaults = {
        'database': f'sqlite:///{tmp_path}/test_db.sqlite3',
        'profiles': []
    }
    config = ConfigManager(defaults=defaults)
    bot = Instabot(config)
    bot.collect()
