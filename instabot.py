import logging.config

from config42 import ConfigManager

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

config_file = "./config.yaml"

def main():
  config = ConfigManager(path='config.yml')
  LOGGER.info(config.get('login'))
  LOGGER.info("Setting configuration from {} : OK".format(config_file))
  print('it works lol')

if __name__ == '__main__':
  main()