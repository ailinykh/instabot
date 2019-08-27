from config42 import ConfigManager
from instabot import Instabot

def test_collect(tmp_path):
    defaults = {
        'database': f'sqlite:///{tmp_path}/test_db.sqlite3',
        'profiles': []
    }
    config = ConfigManager(defaults=defaults)
    bot = Instabot(config)
    bot.collect()
