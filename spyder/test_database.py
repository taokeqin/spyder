import unittest
import database

class DataBaseTests(unittest.TestCase):
    
    def test_db_connect(self):
        db = database.DB()
        self.assertIsNotNone(db)

    def test_db_save_page(self):
        db = database.DB()
        html = "<html>baidu</html>"
        url = "http://www.baidu.com"
        db.save(url, html)
        htmlindb = db.get(url)
        self.assertEqual(html, htmlindb)
