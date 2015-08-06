import unittest
import database
import os
class DataBaseTests(unittest.TestCase):
    
    def setUp(self):
        self.dbname = "test.db"
        self.db = database.DB(self.dbname)

    def tearDown(self):
        self.db.close()
        os.remove(self.dbname)

    def test_db_connect(self):
        self.assertIsNotNone(self.db)

    def test_db_save_page(self):
        html = "<html>baidu</html>"
        url = u"http://www.baidu.com"
        self.db.save(url, html)
        htmlindb = self.db.get(url)
        self.assertEqual(html, htmlindb)
