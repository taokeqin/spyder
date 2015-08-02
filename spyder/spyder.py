import requests
import argparse
import hashlib
from urlparse import urlparse

optparser = argparse.ArgumentParser(description='spyder application.')
optparser.add_argument('-u', '--url', dest='url', help='base url')
args = optparser.parse_args()
if not args.url:
    optparser.print_help()
    quit() 

r = requests.get(args.url)
urlp = urlparse(args.url)
hostname = urlp.netloc
pathname = urlp.path
urlhash = hashlib.sha224(hostname+'/'+pathname).hexdigest()
with open(urlhash, 'w') as f:
    f.write(r.content)
