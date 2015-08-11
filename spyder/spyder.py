# -*- coding: utf-8 -*-
"""
    spyder.py
    ~~~~~~~~~
    This module implements the spyder application.
    :copyright: (c) 2015 by Tao Keqin.
    :license: BSD, see LICENSE for more details.
"""

import sys
import requests
import argparse
import database
import logging
import spydercmd
import threadpool
from threading import Timer


class Downloader(object):
    '''
        impl get method to download url return unicode string
    '''
    def get(self, url):
        '''client use this mehtod to get the html with the given url
        Note: use utf-8 to decode all content
        '''
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
        resp = requests.get(url, headers=headers)
        if resp.encoding != 'utf-8':
            return resp.content.decode(resp.encoding)
        else:
            return resp.text


class Filter(object):
    '''
        impl accept method to check html pass or not
    '''
    def __init__(self, keywords):
        self.keywords = keywords

    def accept(self, html):
        '''client call this metho to check if content pass filter or not'''
        if not self.keywords:
            return True

        result = False
        for keyword in self.keywords:
            if keyword in html:
                result = True
                break

        return result


class Spyder(object):
    '''Main spyder application class
    '''
    def __init__(self):
        self._handle_input()
        self._create_logger()
        self.database = database.DB()
        self.downloader = Downloader()
        self.taskqueue = threadpool.TaskQueue()
        self.threadpool = threadpool.ThreadPool(self.taskqueue, self.threadnumber)
        self.status_timer = None

    def _handle_input(self):
        '''parse and do basic command line validate'''
        optparser = argparse.ArgumentParser(description='spyder application.')
        optparser.add_argument('-u', '--url', dest='url', help='base url')
        optparser.add_argument('-f', dest='logfile', default='spyder.log', help='file to save logs')
        optparser.add_argument('-d', dest='depth', type=int, default=0, help='page depth')
        optparser.add_argument('-k', dest='keywords', help="match key words use or")
        optparser.add_argument('-t', dest='threadnumber', type=int, default=10, help="number of thread in threadpool")
        optparser.add_argument('-l', dest='loglevel', default='warning', choices=['error', 'warning', 'info', 'debug'], help="set the log level: error, warning, info, debug")
        self.args = optparser.parse_args()
        if not self.args.url:
            optparser.print_help()
            quit()
        self.starturl = self.args.url
        self.logfile = self.args.logfile
        self.depth = self.args.depth
        if self.args.keywords:
            self.keywords = [kw.decode(sys.stderr.encoding) for kw in self.args.keywords.split(',')]
        else:
            self.keywords = []
        self.threadnumber = self.args.threadnumber
        levelmap = {"error": logging.ERROR, "warning": logging.WARNING, "info": logging.INFO, "debug": logging.DEBUG}
        self.loglevel = levelmap[self.args.loglevel]

    def _create_logger(self):
        '''create logger with how to print logs'''
        self.logger = logging.getLogger('spyder')
        self.logger.setLevel(self.loglevel)
        filehandler = logging.FileHandler(self.logfile)
        filehandler.setLevel(self.loglevel)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)

    def start(self):
        '''Spyder to start do real work from this method call'''
        htmlfilter = Filter(self.keywords)
        mydepth = 0
        spydertask = spydercmd.SpyderCmd(
            self.starturl,
            mydepth,
            int(self.depth),
            self.downloader,
            self.database,
            self.logger,
            self.taskqueue,
            htmlfilter)
        self.taskqueue.put(spydertask)
        self._print_progress()
        self.threadpool.run()
        print "100% Spyder completed! completed link: ", self.taskqueue.statistics()[0]
        print "Saved {} html page to database.".format(self.database.getsavecounter())

    def _progress(self):
        '''print progress with give format'''
        total, inqueue = self.taskqueue.statistics()
        print "total link: {0}, completed link: {1}, Left in queue: {2}, raw progress: {3}%"\
            .format(total, int(total)-int(inqueue), inqueue, (int(total)-int(inqueue))*1.0/int(total)*100)
        self._print_progress()

    def _print_progress(self):
        '''start a time to print progress every 10s'''
        self.status_timer = Timer(10, self._progress)
        self.status_timer.daemon = True
        self.status_timer.start()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    spyderapp = Spyder()
    spyderapp.start()
