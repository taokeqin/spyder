# -*- coding: utf-8 -*-
"""
    database.py
    ~~~~~~~~~
    This module implements the DB interface.
    :copyright: (c) 2015 by Tao Keqin.
    :license: BSD, see LICENSE for more details.
"""
import sys
import sqlite3
from threading import Lock


class DB(object):
    '''Class represent database access
    '''
    def __init__(self, dbname="data.db"):
        '''init db
        will call connect function to connect to db
        '''
        self.clock = Lock()
        self._connect(dbname)
        self._create_table()

    def save(self, url, html):
        '''Save url, html pair to database'''
        self.clock.acquire()
        try:
            self.cursor.execute("INSERT INTO spyder VALUES(?, ?);", (url, html))
        except:
            print "Unexpected error:", sys.exc_info()
        self.connection.commit()
        self.clock.release()

    def close(self):
        '''close db connection'''
        self.connection.close()

    def get(self, url):
        '''get the html for the given url'''
        self.clock.acquire()
        self.cursor.execute("SELECT html from spyder where url = '{0}'".format(url))
        one = self.cursor.fetchone()
        self.clock.release()
        return one[0]

    def is_url_exist(self, url):
        '''check if give url alread be saved'''
        self.clock.acquire()
        self.cursor.execute("SELECT count(*) from spyder where url = '{0}'".format(url))
        one = self.cursor.fetchone()
        self.clock.release()
        return one[0]

    def _connect(self, filename):
        '''handle connecto to db'''
        self.connection = sqlite3.connect(filename, check_same_thread=False)
        # self.connection.text_factory = str
        self.cursor = self.connection.cursor()

    def _create_table(self):
        '''create the initial table'''
        self.cursor.execute("CREATE TABLE IF NOT EXISTS spyder (url text, html text)")
        self.connection.commit()
