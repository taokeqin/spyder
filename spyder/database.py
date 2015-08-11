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
from decorators import lockguard

class DB(object):
    '''Class represent database access
    '''
    savecounter = 0
    savecounterlock = Lock()
    dblock = Lock()

    def __init__(self, dbname="data.db"):
        '''init db
        will call connect function to connect to db
        '''
        self._connect(dbname)
        self._create_table()

    @lockguard(dblock)
    @lockguard(savecounterlock)
    def save(self, url, html):
        '''Save url, html pair to database'''
        try:
            self.cursor.execute("INSERT INTO spyder VALUES(?, ?);", (url, html))
        except:
            print "Unexpected error:", sys.exc_info()
        self.connection.commit()
        self.savecounter = self.savecounter + 1

    def close(self):
        '''close db connection'''
        self.connection.close()

    @lockguard(dblock)
    def get(self, url):
        '''get the html for the given url'''
        self.cursor.execute("SELECT html from spyder where url = '{0}'".format(url))
        one = self.cursor.fetchone()
        return one[0]

    @lockguard(dblock)
    def is_url_exist(self, url):
        '''check if give url alread be saved'''
        self.cursor.execute("SELECT count(*) from spyder where url = '{0}'".format(url))
        one = self.cursor.fetchone()
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

    @lockguard(savecounterlock)
    def getsavecounter(self):
        return self.savecounter
