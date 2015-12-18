#!/usr/bin/env python
import urllib2 as u
from bs4 import BeautifulSoup as BS

exts=('.gif', '.gifv', '.webm', '.mp4')

def pageToURLs(h):
	return set(map(lambda x:x.replace('.gifv','.mp4'), filter(lambda x: x and any(y in x for y in exts), map(lambda x:x.get('href'), h.select("body a")))))

def getPage(url):
	r=u.Request(url)
	r.add_header('User-Agent','python/testapp 1.0.0')
	f=u.urlopen(r)
	s=f.read()
	f.close()
	return s

def readPages(n=-1):
	url='https://www.reddit.com/r/gifs/'
	while url and n != 0:
		s=getPage(url)
		h=BS(s,'html5lib')
		yield h
		url=(filter(lambda x:x and '&after' in x, map(lambda x:x.get('href'), h.select("body a")))+[None])[0]
		if n>0: n-=1

def main():
	import sys
	for p in readPages():
		print '\n'.join(pageToURLs(p))
		print >>sys.stderr, 'page fetched, enter to continue, q to quit'
		if raw_input()=='q': break
if __name__ == '__main__':main()
