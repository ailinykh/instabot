from config42 import ConfigManager
from instabot import Instabot


def test_collect(tmp_path, mock_request_get):
    defaults = {
        'database': f'sqlite:///{tmp_path}/test_db.sqlite3',
        'collect': {'profiles': ['profile'], 'limit': 100}
    }
    config = ConfigManager(defaults=defaults)
    bot = Instabot(config)
    bot.collect()
