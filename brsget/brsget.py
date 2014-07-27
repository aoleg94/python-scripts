import urllib
import urllib2
import cookielib
from HTMLParser import HTMLParser
import os

URL="http://old.urfu.ru/student/brs/"
CFGFILE="brsget-1.cfg"

class FormParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.url = None
		self.params = {}
		self.in_form = False
		self.form_parsed = False
		self.method = "GET"

	def handle_starttag(self, tag, attrs):
		tag = tag.lower()
		if tag == "form":
			if self.form_parsed:
				raise RuntimeError("Second form on page")
			if self.in_form:
				raise RuntimeError("Already in form")
			self.in_form = True 
		if not self.in_form:
			return
		attrs = dict((name.lower(), value) for name, value in attrs)
		if tag == "form":
			self.url = attrs["action"] 
			if "method" in attrs:
				self.method = attrs["method"].upper()
		elif tag == "input" and "type" in attrs and "name" in attrs:
			if attrs["type"] in ["hidden", "text", "password"]:
				self.params[attrs["name"]] = attrs["value"] if "value" in attrs else ""

	def handle_endtag(self, tag):
		tag = tag.lower()
		if tag == "form":
			if not self.in_form:
				raise RuntimeError("Unexpected end of <form>")
			self.in_form = False
			self.form_parsed = True

_CFGCACHE=None
def getcfg(n,default=None,filter=lambda s:s,raw_input=raw_input):
	global _CFGCACHE
	n=n.strip()
	if _CFGCACHE is None:
		_CFGCACHE={}
		if os.access(CFGFILE,0):
			for line in open(CFGFILE,'r+t'):
				try:
					k,v=map(str.strip,line.split('=',1))
					_CFGCACHE[k]=v
				except ValueError: continue
	if n not in _CFGCACHE:
		v=None
		while v is None:
			v=filter(raw_input("%s: "%n).strip() or default)
		_CFGCACHE[n]=v
		# with open(CFGFILE,'at') as f:
			# print >>f,"%s=%s"%(n,v)
	return _CFGCACHE[n]
	
def clearcfg():
	global _CFGCACHE
	_CFGCACHE=None
	
def putcfg(n,s):
	global _CFGCACHE
	n=n.strip()
	if _CFGCACHE is None:
		_CFGCACHE={}
	_CFGCACHE[n]=s.strip()

def loadcfg(fn):
	global _CFGCACHE
	if _CFGCACHE is not None:
		savecfg()
		_CFGCACHE=None
	global CFGFILE
	CFGFILE=fn
	
def savecfg():
	global _CFGCACHE
	with open(CFGFILE,'wt') as f:
		for kv in _CFGCACHE.iteritems():
			print >>f,"%s=%s"%kv

def request():
	print "downloading form"
	opener = urllib2.build_opener(
		urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
		urllib2.HTTPRedirectHandler())
	f = opener.open(URL)
	s = f.read()
	f.close()
	
	print "filling form"
	parser = FormParser()
	parser.feed(s)
	parser.close()
	if not parser.form_parsed or parser.url is None:
		raise RuntimeError("Something wrong")
	
	parser.params['tx_ustumarks_index[user][username]']=getcfg("User")
	parser.params['tx_ustumarks_index[user][password]']=getcfg("Password")
	parser.params['tx_ustumarks_index[user][email]']=getcfg("Email")
	
	print "posting form"
	assert parser.method=="POST"
	response = opener.open("http://old.urfu.ru/"+parser.url, urllib.urlencode(parser.params))
	print >>open("brsget.txt",'wt'),response.read()
	response.close()
	
def mailget(outf='brs-%s.xls'):
	print "connecting to mail server"
	import imaplib
	import email.parser
	svrhost=getcfg("IMAP4 server address")
	svrport=int(getcfg("IMAP4 server port",993))
	svrssl =getcfg("IMAP4 needs SSL? [y/n]",'y' if svrport==993 else 'n',lambda s:{'y':'y','n':'n','Y':'y','N':'n'}.get(s,None))=='y'
	if svrssl:
		p=imaplib.IMAP4_SSL(svrhost,svrport)
	else:
		p=imaplib.IMAP4(svrhost,svrport)
	p.login(getcfg("Email username"),getcfg("Email password"))
	p.select()
	typ,data=p.search(None,"FROM",'"admin@it.urfu.ru"')
	n = max(map(int,data[0].split()))
	data = p.fetch(n,'(RFC822)')[1][0][1]
	p.shutdown()
	
	print "downloading mail"
	fp = email.parser.FeedParser()
	fp.feed(data)
	msg = fp.close()
	
	import email.utils
	import time
	t=time.mktime(email.utils.parsedate(msg['date']))
	if time.time() - t > 10*60:
		print ' !!! mail is too old, rejecting'
		print ' !!! maybe new mail wasn\'t sent'
		
	# assert len(msg.get_payload())==2
	print "saving files"
	for i,p in enumerate(msg.get_payload()[1:]):
		with open(outf%(i+1),'wb') as f:
			f.write(p.get_payload().replace('\r\n','').decode('base64'))
			print outf%(i+1),
	print
	print 'ok'
	
	
def process():
	import time
	request()
	time.sleep(5.0)
	mailget(getcfg("File mask"))
	
def main2():
	import glob
	for fn in glob.iglob('brsget-*.cfg'):
		loadcfg(fn)
		print '===',fn
		process()
		savecfg()
	print '=== done ==='
	
if __name__=="__main__":
	try:main2()
	finally:		
		import time
		time.sleep(5.0)