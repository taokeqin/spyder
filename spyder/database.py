import sqlite3

class DB:
    
    def __init__(self):
        self._connect()
        self._create_table()

    def save(self, url, html):
        self.c.execute("INSERT INTO spyder VALUES(?, ?)", (url, html))
        self.connection.commit()
        
    def get(self, url):
        self.c.execute("SELECT html from spyder where url = '{0}'".format(url))
        one = self.c.fetchone()
        return one[0]

    def _connect(self, filename="data.sqlite3"):
        self.connection = sqlite3.connect(filename)
        self.connection.text_factory = str
        self.c = self.connection.cursor()

    def _create_table(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS spyder (url text, html text)")
        self.connection.commit()
