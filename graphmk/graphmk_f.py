
def interp(a,b,v):return (v-a)/float(b-a)

def FF(x):
 r=None
 if -2.5<=x<-2: r=(1-interp(-2.5,-2,x))*2
 elif -2<=x<1: r=interp(-2,1,x)*-4
 elif 1<=x<4: r=(1-interp(1,4,x))*-4
 elif 4<=x<6: r=interp(4,6,x)*4
 elif 6<=x<8: r=(4-interp(6,8,x)*2)
 elif 8<=x<=9: r=2+interp(8,9,x)
 return r

def g(L):
	x=yield
	while x is not None:
		for i in xrange(len(L)-1):
			if L[i][0]<=x<=L[i+1][0]: break
		if L[i+1][0]<x or L[i][0]>x: x=yield
		else:
			a,b=L[i],L[i+1]
			(a,c),(b,d)=a,b
			x=yield c+interp(a,b,x)*(d-c)

I=None
lastx=-1e999
def f(x):
	global I,lastx
	if I is None or lastx>x:
		I=g([map(float,l.split()[:2]) for l in open('f.txt')])
		I.next()
	lastx=x
	return I.send(x)
	
def cached(f):
	argcache={}
	def r(*args):
		if args in argcache:return argcache[args]
		else: return argcache.setdefault(args,f(*args))
	return r
	
@cached
def Function(s):
	if isinstance(s,basestring):
		return eval('lambda x: '+s,FN)
	return s
	
def prod(f,x,prec=0.5):
	f=Function(f)
	x-=prec/2
	dy=f(x+prec)-f(x)
	return dy/prec
	
@apply
def nprod():
	cache={}
	def r(n,f,x):
		c=cache.get((n,f))
		if c is None:
			if isinstance(f,basestring): f='(lambda x: %s)'%f#+'(x)'
			else: f=f.__name__
			for i in xrange(n):
				f='(lambda x: prod(%s,x))'%f
			c=cache.setdefault((n,f),eval(f,FN))
		return c(x)
	return r

def nprod_old(n,f,x):
	if isinstance(f,basestring): f='(lambda x: %s)'%f#+'(x)'
	else: f=f.__name__
	s=f
	for i in xrange(n):
		s='(lambda x: prod(%s,x))'%s
	return eval(s,FN)(x)
	
import math,random
FN=vars(random)
FN.update(vars(math))
FN['prod']=prod
FN['nprod']=nprod
FN['f']=f
FN['FF']=FF