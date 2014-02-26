import os
import collections
import pickle

File=collections.namedtuple('File','size time')
Dir=collections.namedtuple('Dir','size time dirs files')
# EmptyDir=Dir(0L,-1.0,{},{})

class Log:
	def __init__(self,fn):
		self.fp=open(fn,'wt',0)
		self.ls=''
	def puts(self,s):
		self.ls=s
		print '\r%s'%s,
	def putnl(self):
		print >>self.fp,self.ls
		print
	def putl(self,s):
		print s
		print >>self.fp,s
	def close(self):
		self.fp.close()

def processFile(root,fn):
	from os.path import getsize, getatime, getmtime, getctime, join
	fqn  = join(root,fn)
	size = getsize(fqn)
	time = max(f(fqn) for f in (getatime, getctime, getmtime))
	return File(size,time)
	
def itergather(path):
	DIRSTAT={}
	for root,dirs,files in os.walk(path, False):
		csize=0
		time=-1.0
		pfiles={}
		for fn in files:
			try:f=processFile(root,fn)
			except Exception: continue
			assert f.size>=0
			csize+=f.size
			if f.time>time:
				time = f.time
			pfiles[fn]=f
		pdirs={}
		for dn in dirs:
			fqdn=os.path.join(root,dn)
			d=DIRSTAT.get(fqdn)
			if d is None: continue
			csize+=d.size
			if d.time>time:
				time = d.time
			pdirs[dn]=d
		DIRSTAT[root]=Dir(csize,time,pdirs,pfiles)
		yield root,DIRSTAT[root]
		
def cligather(log,path="C:\\",dbf='fsinsp.db'):
	def strsize(sz):
		assert sz>=0
		tbl=' KMGTPE'
		for p in xrange(7):
			if p!=6 and sz > 1.1*2**(10*(p+1)): continue
			fsz=sz/(2.0**(10*p))
			return "%.1f %cb"%(fsz,tbl[p])
	root=None
	maxsize=0
	for path,rec in itergather(path.decode('cp1251')):
		root=rec
		if rec.size>maxsize:
			maxsize = rec.size
		try:
			log.puts (u'%s%10s %s'%(strsize(maxsize).ljust(10),strsize(rec.size),path[:57].ljust(57)))
			if rec.size>2**30: log.putnl()
		except UnicodeEncodeError:pass
	log.putnl()
	pickle.dump((path,root),open(dbf,'wb'),-1)	
	
def dbwalk(path,root):
	assert isinstance(root,Dir)
	yield path,root
	for dn,d in root.dirs.itervalues():
		yield os.path.join(path,dn),d
		for pr in dbwalk(os.path.join(path,dn),d):
			yield pr
	
def inspect(log,dbf='fsinsp.db'):
	path,root=pickle.load(open(dbf,'rb'))
	D=[]
	for dn,d in dbwalk(path,root):
		log.puts(dn)
		D.append((d.time,dn,d))
		D+=((f.time,os.path.join(dn,fn),f) for fn,f in d.files.itervalues())
	D=sorted(x for x in D if x[0]>=0)
	log.puts('writing graph')
	f=open('fsinsp.txt','wt')
	a=D[0][0]
	b=D[-1][0]
	ms=max(x[2].size for x in D)
	for t,p,s in D:
		tf=1.0*(t-a)/(b-a)
		sf=1.0*s.size/ms
		x=10*tf
		y=10*sf
		print >>f,x,y
	f.close()
	
		
if __name__ == "__main__": 
	import sys
	log=Log('fsinsp.log')
	cligather(log,*sys.argv[1:2])
	log.close()