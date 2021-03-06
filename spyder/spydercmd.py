# -*- coding: utf-8 -*-
"""
    spydercmd.py
    ~~~~~~~~~
    This module implements the command for spyder task, the command deisgned be run in thread pool.
    :copyright: (c) 2015 by Tao Keqin.
    :license: BSD, see LICENSE for more details.
"""
import copy
import sys
from bs4 import BeautifulSoup
import urlparse
from collections import deque
from threading import Lock
from decorators import lockguard


class SpyderCmd(object):
    '''command for spyder task. must implements execute method'''
    urlcache = deque([], 512)
    urlcachelock = Lock()

    def __init__(self, url, depth, stop_depth, downloader, database, logger, taskqueue, contentfilter):
        self.url = url
        self.netloc = urlparse.urlparse(url).netloc
        self.depth = depth
        self.stop_depth = stop_depth
        self.downloader = downloader
        self.database = database
        self.logger = logger
        self.taskqueue = taskqueue
        self.filter = contentfilter

    @lockguard(urlcachelock)
    def _is_url_exist_in_cache(self, url):
        '''
            this check has two functions:
            1, to speed up the exist url check, if not found, then check in db
            2, to prevent taks in thread working on the same url
        '''
        exist = False
        if url in self.urlcache:
            exist = True
        else:
            self.urlcache.append(url)
        return exist

    def create_subcmd(self, url):
        '''create a subcmd with incremented depth and a given url'''
        subcmd = copy.copy(self)
        subcmd.url = url
        subcmd.depth = self.depth + 1
        return subcmd

    def _extract_links(self, html):
        '''extract all links on currentl html content. currently only support <a> tag'''
        links = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.findAll("a"):
            href = link.get("href")
            if not href:
                continue
            urlparser = urlparse.urlparse(href)
            if urlparser.scheme and urlparser.scheme != "http" and urlparser.scheme != "https":
                continue
            if not urlparser.netloc:
                href = urlparse.urljoin(self.url, href)
            else:
                if urlparser.netloc != self.netloc:
                    # skip this out domain link
                    continue
            href = urlparse.urldefrag(href)[0]
            urlexistincache = self._is_url_exist_in_cache(href)
            if urlexistincache:
                continue
            urlfexistindb = self.database.is_url_exist(href)
            if urlfexistindb:
                continue
            links.append(href)
        return list(set(links))

    def execute(self):
        '''The heave work done in this method.

        download page
        check depth
        check url duplicate
        extrack links
        create sub task for new link
        '''
        try:
            self.logger.info("start download url: {0}".format(self.url))
            html = None
            try:
                html = self.downloader.get(self.url)
            except:
                self.logger.error("download url: {0} failed, with error: {1}".format(self.url, sys.exc_info()[0]))
                raise
            self.logger.info("download url: {0}, commplete!".format(self.url))
            if self.filter.accept(html):
                self.database.save(self.url, html)
                self.logger.info("content of url: {0}, saveed to db".format(self.url))
            else:
                self.logger.warning("content of url: {0}, droped by filter".format(self.url))
            # based on stop level featch all url in current page and create sub cmd
            if self.depth >= self.stop_depth:
                self.logger.debug("currently url: {0} depth reachs the stop depth. will not continue".
                                  format(self.url))
                return
            self.logger.debug("extract urls on page: {0}".format(self.url))

            links = self._extract_links(html)
            self.logger.debug("extract urls on {0} done".format(self.url))
            for href in links:
                self.logger.debug("found new url: {0}, create a sub cmd to download it.".format(href))
                subspyder = self.create_subcmd(href)
                # subspyder.execute()
                self.taskqueue.put(subspyder)
            self.logger.debug("url: {0} process complete!".format(self.url))

        except:
            self.logger.error("download url: {0} failed, with error: {1}".format(self.url, sys.exc_info()))
