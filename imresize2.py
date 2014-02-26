import sys
if not sys.argv[1:]:
	import glob;
	sys.argv[1:] = glob.glob('*.jpg')
	#sys.exit()

import os,thread,Queue
import Image,ImageFile
ImageFile.MAXBLOCK=1024**2

from multiprocessing import cpu_count
CPU_COUNT=cpu_count()

q=Queue.Queue()

def process():
	while not q.empty():
		fn=q.get()
		im=Image.open(fn)
		w,h=im.size
		# im.load()
		im=im.resize((w/2,h/2),Image.ANTIALIAS)
		d,f=os.path.split(fn)
		d+=os.path.sep+'!conv'
		if not os.path.exists(d): os.mkdir(d)
		# im.show()
		im.save(d+os.path.sep+f,quality=50,optimize=1,progressive=1)
		q.task_done()
		sys.stdout.write('.')


for fn in sys.argv[1:]:
	q.put(fn)
for i in xrange(CPU_COUNT):
	thread.start_new(process,())
q.join()

oldtotal=0
newtotal=0

for fn in sys.argv[1:]: 
	d,f=os.path.split(fn)
	print f,
	old=os.path.getsize(fn)
	d+=os.path.sep+'!conv'
	new=os.path.getsize(d+os.path.sep+f)
	print ' %i -> %i (%g%%)'%(old,new,(new*100.0)/old)
	oldtotal+=old
	newtotal+=new

if sys.argv[1:]:
	print 'done.',' %i -> %i (%g%%)'%(oldtotal,newtotal,(newtotal*100.0)/oldtotal)
	import time;time.sleep(1+len(str(len(sys.argv[1:]))))