import json
import os
import pytest
import re
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
        try:
            _, _, _, scope, shortcode, _ = url.split('/')
        except ValueError:
            _, _, _, scope, shortcode = url.split('/')
        
        if scope == 'p':
            filename = f'p_{shortcode}.json'
        elif scope == 'graphql':
            d = json.loads(kwargs["params"]["variables"])
            filename = f'g_{d["shortcode"]}.json'
        else:
            filename = f'u_{scope}.json'

        path = os.path.join(os.path.dirname(__file__), '__mocks__', filename)

        if not os.path.exists(path):
            resp = _get(session, url, **kwargs)
            if 'graphql' in url:
                jsn = json.loads(resp.text)
            else:
                match = re.search(r'window\._sharedData = (.*);</script>', resp.text)
                if match is None:
                    raise Exception("Could not find \"window._sharedData\" in html response.")
                jsn = json.loads(match.group(1))
            open(path, 'w').write(json.dumps(jsn, indent=2))
        
        jsn = json.load(open(path, 'r'))
        resp = requests.Response()
        resp.status_code = 200

        text = json.dumps(jsn)
        
        if not 'graphql' in url:
            text = f'<script type="text/javascript">window._sharedData = {text};</script>'
        
        resp._content = str.encode(text)
        return resp

    _get = requests.Session.get
    monkeypatch.setattr(requests.Session, 'get', mock_get)

def test_collect(tmp_path, mock_request_get):
    defaults = {
        'database': f'sqlite:///{tmp_path}/test_db.sqlite3',
        'profiles': ['space']
    }
    config = ConfigManager(defaults=defaults)
    bot = Instabot(config)
    bot.collect()
