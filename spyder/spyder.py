# -*- coding: utf-8 -*-

import sys
import requests
import argparse
import hashlib
from urlparse import urlparse
import database
import logging
import spydercmd
import threadpool
from threading import Timer

class Downloader:
    def get(self, url):
        headers = {'user-agent': 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
        r = requests.get(url, headers=headers)
        if r.encoding != 'utf-8':
            return r.content.decode(r.encoding)
        else:
            return r.text

class Filter:
    def __init__(self, keywords):
        self.keywords = keywords

    def accept(self, html):
        if not self.keywords:
            return True

        result = False
        for keyword in self.keywords:
            if keyword in html:
                result = True
                break

        return result

class Spyder:

    def __init__(self):
	   self._handle_input()

    def _handle_input(self):
        optparser = argparse.ArgumentParser(description='spyder application.')
        optparser.add_argument('-u', '--url', dest='url', help='base url')
        optparser.add_argument('-f', dest='logfile', help='file to save logs')
        optparser.add_argument('-d', dest='depth', help='page depth')
        optparser.add_argument('-k', dest='keywords', help="match key words use or")
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
        if self.args.keywords:
            self.keywords = [s.decode(sys.stderr.encoding) for s in self.args.keywords.split(',')]
        else:
            self.keywords = []


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
        #f = Filter([u"云计算"])
        f = Filter(self.keywords)
        mydepth = 0
        self.spydercmd = spydercmd.SpyderCmd(self.starturl, mydepth, \
                        int(self.depth), self.downloader, \
                        self.db, self.logger, self.taskqueue, f)
        self.taskqueue.put(self.spydercmd)
        self.print_progress()
        self.tp.run()
        print "100% Spyder completed!"
        
    def progress(self):
        total, inqueue = self.taskqueue.statistics()
        print "total link: {0}, completed link: {1}, Left in queue: {2}, raw progress: {3}%"\
            .format(total, int(total)-int(inqueue), inqueue, (int(total)-int(inqueue))*1.0/int(total)*100)
        self.print_progress()

    def print_progress(self):
        self.t=Timer(10,self.progress)
        self.t.daemon = True
        self.t.start()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    s = Spyder()
    s.start()
