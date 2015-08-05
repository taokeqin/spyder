import unittest
import spydercmd
import copy
from mock import MagicMock, call

class DownloaderMock:
    pass
    

class DataBaseMock:
    pass

class Logger:
    pass

class SpyderCmdTests(unittest.TestCase):
    
    def setUp(self):
        self.logger = Logger()
        self.logger.info = MagicMock()
        self.logger.debug = MagicMock()
        self.logger.error = MagicMock()

    def test_spyder_depth(self):
        # url, url_depth, message_queue, db, logger
        s = spydercmd.SpyderCmd("http:://www.baidu.com", 0, 2, None, None, self.logger)
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

        s = spydercmd.SpyderCmd(u"http://a.com/0.html", 0, 2, dlmock, db, self.logger)
        s.execute()
        
        dlmock.get.assert_has_calls([call(u"http://a.com/0.html"),
                                     call(u"http://a.com/1.html")])
        db.save.assert_has_calls(
            [call(u"http://a.com/0.html",'<a href="http://a.com/1.html">'),
            call(u"http://a.com/1.html", 'nolink')])
        
    def test_execute_stop_when_reach_stopdepth(self):
        dlmock = DownloaderMock()       
        dlmock.get = MagicMock(side_effect=['<a href="http://a.com/11.html">',
                                            '<a href="http://a.com/21.html">',
                                            '<a href="http://a.com/31.html">',
                                            '<a href="http://a.com/41.html">'])
        db = DataBaseMock()
        db.save = MagicMock()
        db.is_url_exist = MagicMock(return_value=False)
        s = spydercmd.SpyderCmd(u"http://a.com/0.html", 0, 2, dlmock, db, self.logger)
        s.execute()
        
        dlmock.get.assert_has_calls([call(u"http://a.com/0.html"),
                                     call(u"http://a.com/11.html")])
        db.save.assert_has_calls(
            [call(u"http://a.com/0.html", '<a href="http://a.com/11.html">'),
             call(u"http://a.com/11.html", '<a href="http://a.com/21.html">'),
            call(u"http://a.com/21.html", '<a href="http://a.com/31.html">')])