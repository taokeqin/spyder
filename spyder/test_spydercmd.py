import unittest
import spydercmd
import copy
from mock import MagicMock, call
from Queue import Queue

class DownloaderMock:
    pass
    

class DataBaseMock:
    pass

    
class Logger:
    pass

    
class Filter:
    pass
    
    
class SpyderCmdTests(unittest.TestCase):
    
    def setUp(self):
        self.logger = Logger()
        self.logger.info = MagicMock()
        self.logger.debug = MagicMock()
        self.logger.error = MagicMock()
        self.queue = Queue()
        self.filter = Filter()
        self.filter.accept = MagicMock()
        
    def test_spyder_depth(self):
        # url, url_depth, message_queue, db, logger
        s = spydercmd.SpyderCmd("http:://www.baidu.com", 0, 2, None, None, self.logger, self.queue, self.filter)
        self.assertEqual(s.depth, 0)
        subspyder = s.create_subcmd("http://www.google.com")
        self.assertEqual(subspyder.depth, 1)
        subsubspyder = subspyder.create_subcmd("http://www.bing.com")
        self.assertEqual(subsubspyder.depth, 2)
        
    def test_execute_stop_when_no_link(self):
        dlmock = DownloaderMock()
        dlmock.get = MagicMock(side_effect=['<a href="http://a.com/1.html">', 'nolink'])

        db = DataBaseMock()
        db.save = MagicMock()
        db.is_url_exist = MagicMock(return_value=False)

        s = spydercmd.SpyderCmd(u"http://a.com/0.html", 0, 2, dlmock, db, self.logger, self.queue, self.filter)
        s.execute()
        
        self.assertEqual(self.queue.qsize(), 1)
        
    def test_execute_stop_when_reach_stopdepth(self):
        dlmock = DownloaderMock()       
        dlmock.get = MagicMock(side_effect=['<a href="http://a.com/11.html">',
                                            '<a href="http://a.com/21.html">',
                                            '<a href="http://a.com/31.html">',
                                            '<a href="http://a.com/41.html">'])
        db = DataBaseMock()
        db.save = MagicMock()
        db.is_url_exist = MagicMock(return_value=False)
        s = spydercmd.SpyderCmd(u"http://a.com/0.html", 0, 2, dlmock, db, self.logger, self.queue, self.filter)
        s.execute()
        
        self.assertEqual(self.queue.qsize(), 1)