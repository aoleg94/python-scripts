import urllib2

def strsize(sz):
	assert sz>=0
	tbl=' KMGTPE'
	for p in xrange(7):
		if p!=6 and sz > 1.1*2**(10*(p+1)): continue
		fsz=sz/(2.0**(10*p))
		return "%.2f %cb"%(fsz,tbl[p])
	
def putlr(s):
	print '\r %s'%(s+' '*80)[:77],

class TrafficWatcher:
	NUM_SAMPLES=10
	def __init__(self):
		self.nb=0
		self.lastCall=None
		self.samples=[]
	def start(self):
		from time import clock
		self.lastCall = clock()
	def add(self,dnb):
		from time import clock
		self.nb+=dnb
		now=clock()
		dt=now - self.lastCall
		self.lastCall=now
		# if self.lastCall == -1:
			# self.lastCall = now
			# dnb = 0
		self.samples.insert(0,dnb/dt)
		self.samples=self.samples[:TrafficWatcher.NUM_SAMPLES]
	@property
	def speed(self):
		return sum(self.samples)/len(self.samples)
	
	class FileWrapper:
		def __init__(self,fp,tw):
			self.fp=fp
			self.tw=tw
			tw.start()
		def read(self,*x):
			s=self.fp.read(*x)
			self.tw.add(len(s))
			return s
		def __getattr__(self,n):
			return getattr(self.fp,n)
			
	def wrap(self,fp):
		return TrafficWatcher.FileWrapper(fp,self)
	def iter(self,it,cb=lambda *x:''):
		for x in it:
			putlr('%s dl (%s/s)%s'%(strsize(self.nb),strsize(self.speed),cb(x)))
			yield x
		print
	def watch(self,*x):
		for y in self.iter(*x):pass
		
trafficWatcher = TrafficWatcher()

class fileOpener:
	def __init__(self,zipfn):
		self.zipfn=zipfn
	def read(self,r):
		s=r.headers.get('Range','bytes=0-')
		start,end=s[6:].split('-')
		with open(self.zipfn,'rb') as f:
			if start:
				start=int(start)
				end=int(end or -1)
				f.seek(start)
				if end:
					return f.read(int(end)-start+1)
				else:
					return f.read()
			else:
				assert end
				end=int(end)
				f.seek(-end,2)
				return f.read()
	def open(self,r):
		import cStringIO
		f=cStringIO.StringIO(self.read(r))
		class asdasd:
			def __init__(self,f):
				self.f=f
			def __getattr__(self,n):
				return getattr(self.f,n)
			def getcode(self):
				return 206
		return asdasd(f)

def rangeConv(range):
	if len(range)==1:
		x=range[0]
		if x>=0: return 0,x
		elif x<0: return '',-x
		# else: 
	elif len(range)==2:
		x,y=range
		return x,x+y-1
	elif len(range)==3:
		x,y,z=range
		assert x<y
		return x,y
	else:
		raise TypeError('need 1-, 2- or 3-tuple for range')
		
def rangeToHeader(range):
	if isinstance(range,int):range=(range,)
	return 'bytes=%s-%s'%rangeConv(range)
	
def getFilePart1(range,url,data=None,headers=None,opener=None):
	if headers is None: headers={}
	r=urllib2.Request(url,data,headers)
	r.add_header('Range',rangeToHeader(range))
	# r.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')
	nretries=5
	while nretries:
		try:
			if opener is None:
				f=urllib2.urlopen(r)
			else:
				f=opener.open(r)
			break
		except Exception,e: 
			print "%s: %s"%(e.__class__.__name__,', '.join(map(str,e.args)))
			nretries-=1
			from time import sleep
			sleep(5)
	assert f.getcode()==206,'Server does not support partial file download (%i)'%f.getcode()
	return trafficWatcher.wrap(f)
		
def getFilePart(*x):
	import contextlib
	return contextlib.closing(getFilePart1(*x))
	
def readStruct(f,fmt):
	import struct
	l=struct.calcsize(fmt)
	s=f.read(l)
	if l!=0 and s=='':
		raise EOFError
	return struct.unpack(fmt,s)
	
def readEOCD(f):
	sig,ndisk,cdisk,ncr,tcr,szcd,ofscd,comlen=readStruct(f,'<IHHHHIIH')
	assert sig==0x06054b50
	assert ndisk==cdisk==comlen==0
	assert ncr==tcr
	return ofscd,szcd
	
def readCD1(f):
	x=sig,verm,vern,gpflag,compm,flmt,flmd,crc32,csize,usize,fnlen,exlen,fclen,diskn,infattr,exfattr,lfhrofs=readStruct(f,'<IHHHHHHIIIHHHHHII')
	assert sig==0x02014b50
	assert diskn==0
	fn=f.read(fnlen)
	ex=f.read(exlen)
	fc=f.read(fclen)
	return x+(fn,ex,fc)
	
def readCD(f):
	x=sig,verm,vern,gpflag,compm,flmt,flmd,crc32,csize,usize,fnlen,exlen,fclen,diskn,infattr,exfattr,lfhrofs=readStruct(f,'<IHHHHHHIIIHHHHHII')
	assert sig==0x02014b50
	assert diskn==0
	assert compm in (0,8) # deflated
	fn=f.read(fnlen)
	ex=f.read(exlen)
	fc=f.read(fclen)
	return fn,lfhrofs,csize,usize
	
def parseLFH(fname,offset,csize1,usize1,*args):
	fsize=csize1,usize1
	size=30
	with getFilePart((offset,size),*args) as f:
		sig,vern,gpflag,compm,flmt,flmd,crc32,csize,usize,fnlen,exlen=readStruct(f,'<IHHHHHIIIHH')
		assert sig==0x04034b50
		assert compm in (0,8) # deflated
		# assert (csize,usize)==0 or (csize,usize)==fsize
		fn=f.read(fnlen)
		ex=f.read(exlen)
		# print fn,fname
		# assert fn==fname
		return (fname,offset+size+fnlen+exlen,csize1,usize1)
	
def parseZip(url,data=None,headers=None,opener=None):
	args=url,data,headers,opener
	with getFilePart(-22,*args) as f:
		offset,size=readEOCD(f)
	with getFilePart((offset,size),*args) as f:
		try:
			while 1:
				fn,ofs,csize,usize=readCD(f)
				yield (fn,ofs,csize,usize)
				# yield parseLFH(fn,ofs,fsize,*args)
		except EOFError: pass
	
def buildFS(root,stream):
	import os
	for fn,ofs,csize,usize in stream:
		p=os.path.join(root,fn)
		d=os.path.dirname(p)
		try:os.makedirs(d)
		except OSError:pass
		if os.path.isdir(p): continue
		with open(p,'wb') as f: f.write('\0'*usize)
		yield fn
		
def checkAndDownload(root,stream,*args):
	import os,contextlib
	for fn,ofs,csize,usize in stream:
		p=os.path.join(root,fn)
		d=os.path.dirname(p)
		if os.path.isdir(p): continue
		if os.access(p,0):
			fn,ofs,csize,usize=parseLFH(fn,ofs,csize,usize,*args)
			with contextlib.nested(getFilePart((ofs,csize),*args), open(p,'wb')) as (fin,fout):
				inflate(csize,usize,fin,fout)
				yield fn

def inflate(csize,usize,fin,fout):
	CHUNKSIZE=64*1024
	if csize==usize: # assume data is uncompressed in this case
		while csize:
			s=fin.read(min(csize,CHUNKSIZE))
			fout.write(s)
			csize-=len(s)
	else:
		import zlib
		d=zlib.decompressobj(-15)
		while csize:
			s=fin.read(min(csize,CHUNKSIZE))
			fout.write(d.decompress(s))
			csize-=len(s)
		# s=fin.read(csize)
		fout.write(d.flush())

	
def main(url=None, root=None, noreload=False):
	if url is None and root is None:
		print 'usage: zipdl.py [<url> [<folder> [<noreload>]]]'
		print '    if <noreload> is present, the program will download immediately, as if tree was built already'
		print
		
	url=url or raw_input('Enter URL for zip file to inspect: ')
	root=root or raw_input('Enter folder in which file tree will be built: ')
	assert url and root, "URL and folder name cannot be empty"
	
	print 'downloading zip header'
	L=[]
	for x in trafficWatcher.iter(parseZip(url),lambda *x: ', %i entries read'%(len(L)+1)):
		L.append(x)
		
	if not noreload:
		print 'building file tree'
		# trafficWatcher.watch(buildFS(root,L),lambda fn:', '+fn)
		for fn in buildFS(root,L):
			putlr(fn)
		print
		print "done building tree"
		print "Now go and explore %s, delete files you don't want to download"%root
		raw_input("Press Enter to begin downloading and extracting files")
		
	trafficWatcher.watch(checkAndDownload(root,L,url),lambda fn:', '+fn)
	print 'done'
	
if __name__=='__main__':
	import sys
	main(*sys.argv[1:4])