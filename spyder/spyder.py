import requests
import argparse
import hashlib
from urlparse import urlparse
import database
import logging

class Spyder:

    def __init__(self):
	   self._handle_input()

    def _handle_input(self):
        optparser = argparse.ArgumentParser(description='spyder application.')
        optparser.add_argument('-u', '--url', dest='url', help='base url')
        optparser.add_argument('-f', dest='logfile', help='file to save logs')
        self.args = optparser.parse_args()
        if not self.args.url:
            optparser.print_help()
            quit()
        self.starturl = self.args.url
        if not self.args.logfile:
            self.logfile = 'spyder.log'
        else:
            self.logfile = self.args.logfile


    def _create_logger(self):
        self.logger = logging.getLogger('spyder')
        self.logger.setLevel(logging.INFO)
        h = logging.FileHandler(self.logfile)
        h.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        h.setFormatter(formatter)
        self.logger.addHandler(h)

    def start(self):
        self._create_logger()
        self.logger.info("download page: {0}".format(self.starturl))
        self.r = requests.get(self.starturl)
        self.db = database.DB()
        self.db.save(self.starturl, self.r.content)

if __name__ == "__main__":
    s = Spyder()
    s.start()
