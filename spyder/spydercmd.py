import copy
import sys
from bs4 import BeautifulSoup
import urlparse

class SpyderCmd:
    
    def __init__(self, url, depth, stop_depth, downloader, database, logger):
        self.url = url
        self.netloc = urlparse.urlparse(url).netloc
        self.depth = depth
        self.stop_depth = stop_depth
        self.downloader = downloader
        self.database = database
        self.logger = logger

    def create_subcmd(self, url):
        subcmd = copy.copy(self)
        subcmd.url = url
        subcmd.depth = self.depth + 1
        return subcmd
    
    def _extract_links(self, html):
        links = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.findAll("a"):
            href = link.get("href")
            up = urlparse.urlparse(href)
            if not up.netloc:
                href = urlparse.urljoin(self.url, href)
            else:
                if up.netloc != self.netloc:
                    #skip this out domain link
                    continue
            href = urlparse.urldefrag(href)[0]
            urlfexistindb = self.database.is_url_exist(href)
            if urlfexistindb:
                continue
            links.append(href)
        return list(set(links))

    def execute(self):
        try:
            self.logger.info("start download url: {0}".format(self.url))
            html = self.downloader.get(self.url)
            self.logger.info("download url: {0}, commplete!".format(self.url))
            self.database.save(self.url, html)
            self.logger.debug("content of url: {0}, saveed to db".format(self.url))
            #based on stop level featch all url in current page and create sub cmd
            if self.depth >= self.stop_depth:
                self.logger.debug("currently url: {0} depth reachs the stop depth. will not continue".format(self.url))
                return
            self.logger.debug("extract urls on page: {0}".format(self.url))

            links = self._extract_links(html)
            for href in links:
                self.logger.debug("found new url: {0}, create a sub cmd to download it.".format(href))
                subspyder = self.create_subcmd(href)
                subspyder.execute()
            self.logger.info("url: {0} process complete!".format(self.url))

        except:
            self.logger.error("download url: {0} failed, with error: {1}".format(self.url, sys.exc_info()))