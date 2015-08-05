import sys
import sqlite3
from threading import Lock

class DB:
    
    def __init__(self, dbname="data.sqlite3"):
        self.clock = Lock()
        self._connect(dbname)
        self._create_table()

    def save(self, url, html):
        self.clock.acquire()
        try:
            r = self.c.execute("INSERT INTO spyder VALUES(?, ?);", (url, html))
        except:
            print "Unexpected error:", sys.exc_info()
        self.connection.commit()
        self.clock.release()
        
    def get(self, url):
        self.clock.acquire()
        self.c.execute("SELECT html from spyder where url = '{0}'".format(url))
        one = self.c.fetchone()
        self.clock.release()
        return one[0]
        
    def is_url_exist(self, url):
        self.clock.acquire()
        self.c.execute("SELECT count(*) from spyder where url = '{0}'".format(url))
        one = self.c.fetchone()
        self.clock.release()
        return one[0]

    def _connect(self, filename):
        self.connection = sqlite3.connect(filename, check_same_thread=False)
        self.connection.text_factory = str
        self.c = self.connection.cursor()

    def _create_table(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS spyder (url text, html text)")
        self.connection.commit()