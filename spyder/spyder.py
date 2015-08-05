import requests
import argparse
import hashlib
from urlparse import urlparse
import database
import logging
import spydercmd
import threadpool

class Downloader:
    def get(self, url):
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.content


class Spyder:

    def __init__(self):
	   self._handle_input()

    def _handle_input(self):
        optparser = argparse.ArgumentParser(description='spyder application.')
        optparser.add_argument('-u', '--url', dest='url', help='base url')
        optparser.add_argument('-f', dest='logfile', help='file to save logs')
        optparser.add_argument('-d', dest='depth', help='page depth')
        self.args = optparser.parse_args()
        if not self.args.url:
            optparser.print_help()
            quit()
        self.starturl = self.args.url
        if not self.args.logfile:
            self.logfile = 'spyder.log'
        else:
            self.logfile = self.args.logfile
        if not self.args.depth:
            self.depth = 0
        else:
            self.depth = self.args.depth


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
        self.db = database.DB()
        self.downloader = Downloader()
        self.taskqueue = threadpool.TaskQueue()
        self.tp = threadpool.ThreadPool(self.taskqueue)
        self.spydercmd = spydercmd.SpyderCmd(self.starturl, 0, int(self.depth), self.downloader, self.db, self.logger, self.taskqueue)
        #self.spydercmd.execute()
        self.taskqueue.put(self.spydercmd)
        self.tp.run()
        print self.taskqueue.statistics()

if __name__ == "__main__":
    s = Spyder()
    s.start()
