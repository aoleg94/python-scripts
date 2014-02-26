import re
from urllib2 import urlopen,unquote
import thread,Queue

m=re.compile(r'<li><a href="(.*?)(/?)">')

def walkpage(root,url):
	print 'Fetching',url
	f=urlopen(root+url)
	s=f.read()
	f.close()
	for p,d in m.findall(s):
		if p=='..': continue
		if d=='/': 
			for f in walkpage(root,url+p+'/'):
				yield f
		else: yield url,p
		
def gather(root,localdir='',keep=False):
	import sys,os
	#o=open(sys.argv[2],'w') if len(sys.argv)>2 else sys.stderr
	root=root.strip('/')+'/'
	# localdir=sys.argv[2] if len(sys.argv)>=2 else ''
	for d,f in walkpage(root,''):
		#print >>o,d,f,root+d+f
		L=[localdir]
		L+=d.strip('/').split('/')
		l=unquote(os.path.join(*L))
		if l and not os.access(l,0):
			os.makedirs(l)
		fp=os.path.join(l,unquote(f))
		if keep and os.access(fp,os.R_OK): continue
		yield fp,root+d+f
		# f=open(os.path.join(l,unquote(f)),'wb')
		# s=urlopen()
		# f.write(s.read())
		# f.close()
		# s.close()
		
global NotReady
NotReady=True
def dlworker(q):
	BLOCKSIZE=2**17
	global NotReady
	while not q.empty() or NotReady:
		fn,url=q.get()
		# print "%79s\r"%fn,
		f=open(fn,'wb')
		s=urlopen(url)
		d=s.read(BLOCKSIZE)
		while d:
			f.write(d)
			d=s.read(BLOCKSIZE)
		f.close()
		s.close()
		q.task_done()
		
if __name__=='__main__':
	import sys
	num_workers=4
	try: 
		num_workers=int(sys.argv[1])
		del sys.argv[1]
	except ValueError:pass
	q=Queue.Queue(num_workers)
	it=gather(*sys.argv[1:])
	for i,v in zip(xrange(num_workers),it):
		q.put(v)
	for i in xrange(num_workers):
		thread.start_new(dlworker,(q,))
	for v in it:
		q.put(v)
	global NotReady
	NotReady = False
	q.join()
	# if len(L)==num_workers:
		# try:
			
	# elif len(L)<=num_workers:
		# try
		# for i,v in L: q.put(v)
		# dlworker(q)
	
	
	