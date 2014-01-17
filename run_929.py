from argparse import ArgumentParser
import sys

from pybloomfilter import BloomFilter

from nine_two_nine.util import load_config
from nine_two_nine.monitor import Monitor
from threading import Thread

def main(args):
  parser = ArgumentParser(description=main.__doc__)
  parser.add_argument('--config', '-c', 
                      help="Path to configuration file",
                      default=None)
  pargs = parser.parse_args(args)

  config = load_config(__name__, pargs.config)

  bloom_filter = BloomFilter.open(config['nine_two_nine']['bloom_filter'])

  sites = ['http://www.930.com/concerts/']

  monitor = Monitor(sites,
                    config['nine_two_nine']['from_email'],
                    config['nine_two_nine']['to_email'],
                    config['nine_two_nine']['username'],
                    config['nine_two_nine']['password'],
                    bloom_filter,
                    config['nine_two_nine']['sleeptime'])

  monitor.notify_via_email("this is a link")

if __name__ == '__main__':
  main(sys.argv[1:])