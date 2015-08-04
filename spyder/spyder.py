import requests
import argparse
import hashlib
from urlparse import urlparse

class Spyder:

    def __init__(self):
	self._handle_input()

    def _handle_input(self):
        optparser = argparse.ArgumentParser(description='spyder application.')
        optparser.add_argument('-u', '--url', dest='url', help='base url')
        self.args = optparser.parse_args()
        if not self.args.url:
            optparser.print_help()
            quit() 

    def start(self):
        self.r = requests.get(self.args.url)
        urlp = urlparse(self.args.url)
        hostname = urlp.netloc
        pathname = urlp.path
        urlhash = hashlib.sha224(hostname+'/'+pathname).hexdigest()
        with open(urlhash, 'w') as f:
            f.write(self.r.content)

if __name__ == "__main__":
    s = Spyder()
    s.start()
