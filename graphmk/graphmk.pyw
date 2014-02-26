# -*- coding: utf-8 -*-
from Tkinter import Tk,Frame,Canvas,Scrollbar,Label,Button,Checkbutton,Entry, \
	HORIZONTAL,VERTICAL,RIGHT,LEFT,BOTH,X,Y,TOP,StringVar,IntVar
from decimal import Decimal as dec
import math,random,sys,os,time

WINMOBILE = (sys.platform=='win32' and os.name=='ce')
CELLSIZE  = 32
_1_CELLSIZE = 1.0/CELLSIZE
FRAMERATE = 5*CELLSIZE
MAX_REAL=1e2 #16331239353195370.0

WW,HH=640,400 #220,230 # размеры окна
W,H=2432,1600 # размеры поверхности
# WW_PC,HH_PC=640,640

r=Tk() # создаём окно..
r.title(u'Построитель графиков функций')
f=Frame() # фрейм..
c=Canvas(f,width=WW,height=HH,bg='white',scrollregion=(0,0,W,H)) # поверхность..
sX=Scrollbar(r,orient=HORIZONTAL) # скроллбары
sY=Scrollbar(f,orient=VERTICAL)
c['xscrollcommand']=sX.set
c['yscrollcommand']=sY.set
sX['command']=c.xview
sY['command']=c.yview
c.pack(fill=BOTH,side=LEFT,expand='1')
sY.pack(fill=Y,side=RIGHT)
f.pack(expand='1',fill=BOTH)
c.xview_moveto((W/2.0-WW/2.0)/W)
c.yview_moveto((H/2.0-HH/2.0)/H)
sX.pack(fill=X,side=TOP)
form=StringVar()
f=Frame(r)
Label(f,text='y=').pack(side=LEFT) # текстовое поле..
e=Entry(f,textvar=form)
e.pack(fill=X,side=LEFT,expand='1')
noclear=IntVar()
noclear.set(0)
Checkbutton(f,variable=noclear).pack(side=RIGHT)
f.pack(fill=X)
L=[]


FN=vars(random)
FN.update(vars(math))

def Func(f):
	if isinstance(f,basestring):
		def fff(g):
			FN[f]=g
		return fff
	FN[f.__name__]=f
	
#----------------------------------------------------------

def interp(a,b,v):return (v-a)/float(b-a)

@Func
def FF(x):
 r=None
 if -2.5<=x<-2: r=(1-interp(-2.5,-2,x))*2
 elif -2<=x<1: r=interp(-2,1,x)*-4
 elif 1<=x<4: r=(1-interp(1,4,x))*-4
 elif 4<=x<6: r=interp(4,6,x)*4
 elif 6<=x<8: r=(4-interp(6,8,x)*2)
 elif 8<=x<=9: r=2+interp(8,9,x)
 return r

@Func
def root(n,x,m=1.0):
	return (x**float(m))**(1.0/n) if x>=0 else -((-x)**float(m))**(1.0/n)
 
@Func
def curt(x):
	return x**(1/3.0) if x>=0 else -(-x)**(1/3.0)
	
 
I=None
lastx=-1e999

@Func('f')
@apply
def fromfile():
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

	# I=None
	# lastx=-1e999
	def f(x,fn='f.txt'):
		global I,lastx
		if I is None or lastx>x:
			I=g([map(float,l.split()[:2]) for l in open(fn)])
			I.next()
		lastx=x
		return I.send(x)
	return f
	
	
_GLOBALCACHE=[]
def cached(f):
	argcache={}
	global _GLOBALCACHE
	_GLOBALCACHE.append(argcache)
	def r(*args):
		if args in argcache:return argcache[args]
		else: return argcache.setdefault(args,f(*args))
	return r
	
_GLOBALCACHE_CLEAR_TIME=-1
@Func
def clearcache(a=None):
	global _GLOBALCACHE, _GLOBALCACHE_CLEAR_TIME
	import time
	t=time.time()
	if _GLOBALCACHE_CLEAR_TIME+1>t:
		for x in _GLOBALCACHE:
			x.clear()
		_GLOBALCACHE_CLEAR_TIME=t
	return a
	
@cached
def Function(s):
	if isinstance(s,basestring):
		return eval('lambda x: '+s,FN)
	return s
	
def valid(y): return isinstance(y,bool) or y is None or not isinstance(y,(float,int,long))

def ev(f,a,b,errors,prec=0.1):
	f=Function(f)
	dx=prec
	x=a-dx
	while x<b:
		x+=dx
		try:
			y=f(x)
			if valid(y):
				yield None,None
				continue
		except Exception,e:
			if not isinstance(e,(ArithmeticError,ValueError)):
				errors.add('%s: %s'%(e.__class__.__name__,e))
			yield None,None
			continue
		try:
			y1=f(x+dx)
			if valid(y1):
				yield None,None
				continue
		except Exception,e:
			if not isinstance(e,(ArithmeticError,ValueError)):
				errors.add('%s: %s'%(e.__class__.__name__,e))
			yield None,None
			continue
			
			yield x,y
			dy=y1-y
			if abs(dy)<prec: dx=prec
			else: dx/=sqrt(dx*dx+dy*dy)
			x+=dx
	
# @Func('prim')
# @apply
# def prim():
	# cache={}
	# def r(f,x,prec=0.1):
		

@Func
def diff(f,x,prec=0.1):
	f=Function(f)
	x-=prec/2
	dy=f(x+prec)-f(x)
	return dy/prec
	
	
@Func('ndiff')
@apply
def ndiff():
	cache={}
	def r(n,f,x):
		c=cache.get((n,f))
		if c is None:
			if isinstance(f,basestring): f='(lambda x: %s)'%f#+'(x)'
			else: f=f.__name__
			for i in xrange(n):
				f='(lambda x: diff(%s,x))'%f
			c=cache.setdefault((n,f),eval(f,FN))
		return c(x)
	return r


@Func
def limitD(a,b,f,x):
	f=Function(f)
	if a<=x<=b:return f(x)
	
@Func
def limitE(a,b,f,x):
	f=Function(f)
	r=f(x)
	if a<=r<=b:return r
	
@Func
def clamp(a,b,f,x):
	f=Function(f)
	r=f(x)
	if r>b:return b
	elif r<a:return a
	return r

@Func
def bar(X,x):
	return ((x>=X)*2-1)*H*2
	
@Func
def dot(X,Y,x):
	if abs(x-X)<2*_1_CELLSIZE:return Y
	

@cached
def Series(s,n=None):
	if isinstance(s,basestring):
		if n is None: 
			return cached(eval('lambda n: lambda x: '+(s),FN))
		else:
			return (eval('lambda n: lambda x: '+(s),FN))(n)
	return s
	
@Func
def series(n,f,x):
	return Series(f,n)(x)
	
@cached
def fsum(f,n,fi):
	fa=[Series(f,N) for N in xrange(fi,fi+n)]
	def r(x):
		return sum(f(x) for f in fa)
	return r

@Func
def seriessum(n,f,x,fi=0):
	return fsum(f,n,fi)(x)
	
@cached # n >= 0
def rawfact(n):
	if n<2: return 1
	else: 
		group = n >> 7
		rem = n & 127
		if not rem: group -= 1
		base = group << 7
		v = rawfact(base)
		for m in xrange(rem):
			v *= base+m+1
		return v
		
@Func
def fact(x):
	n=abs(int(x+0.5))
	return rawfact(n)
	
def integr(f,a,b,h=_1_CELLSIZE):
	l=int((b-a)/h+0.5)
	if l<0:return -integr(f,b,a,h)
	f=Function(f)
	return sum(f(a+s*h)*h for s in xrange(l+1))
Func(integr)
#----------------------------------------------------------

def hsv2rgb(h,s,v):
	Hi=(h//60)%6
	f=h/60.-h//60
	p=v*(1-s)*255
	q=v*(1-f*s)*255
	t=v*(1-(1-f)*s)*255
	v*=255
	if   Hi==0: return v,t,p
	elif Hi==1: return q,v,p
	elif Hi==2: return p,v,t
	elif Hi==3: return p,q,v
	elif Hi==4: return t,p,v
	elif Hi==5: return v,p,q

@apply
def colors():
	yield
	H=0
	S=1
	V=1
	yield 255,0,0
	while 1:
		H+=100
		if H>=3600:
			V=(V-0.5)*0.75+0.5
			H=0
		while (yield hsv2rgb(H,S,V)):
			H=-100
			S=1
			V=1
colors.next()

def proc(*args): # здась вся соль программы
	s=form.get()
	if s.strip()=='': return # если функция не дана, то ничего не делаем
	try: f=Function(s)
	except Exception,e:
		import tkMessageBox
		tkMessageBox.showerror(title=u'Ошибка разбора',message=str(e))
		return
	global L
	if not noclear.get():
		for idx in L:
			c.delete(idx) # чистим поверхность от прошлого графика
		L[:]=[]
		colors.send(True)
		color  = 'black'
	else:color = '#%02x%02x%02x'%colors.next()
	line=1 # флаг соединения точек (для случая x=0 в y=k/x)
	x=px=-W*_1_CELLSIZE # начинаем рисовать за окном
	
	try:
		py=f(x) # вычисляем
	except Exception,e:
		line=0 # если не вычисляется, то не рисуем пока
	errors=set()
	time=0
	for xx in xrange(-W,W): 
		x=xx*_1_CELLSIZE
		try:
			y=f(x) # вычисляем
			if isinstance(y,bool) or y is None or not isinstance(y,(float,int,long)):
				line=0
				continue
			if abs(y)>MAX_REAL:
				line=0
				continue
			if line: # если предыдущая точка существует
				L.append(c.create_line((px*CELLSIZE)+W/2,(-py*CELLSIZE)+H/2,(xx)+W/2,(-y*CELLSIZE)+H/2,width=1.5,fill=color))
				# то рисует линию из той в текущую точку
				time+=1
				if time > FRAMERATE: 
					r.update_idletasks() # обновляем вид, чтоб на кпк не зависало
					time=0
			px,py=x,y # сохраняем точку
			line=1 # как существующую
		except Exception,e: # если ошибка
			line=0 # то этой точки в графике не будет
			if not isinstance(e,(ArithmeticError,ValueError,TypeError)):
				errors.add('%s: %s'%(e.__class__.__name__,e))
			continue
		import tkMessageBox
	if errors: 
		s=u'Ошибки при вычислении:\n'
		for e in errors: s+='  %s\n'%e
		tkMessageBox.showerror(title=u'Ошибки',message=s)
# и так пока все точки не пройдем
e.bind('<Key-Return>',proc) # по нажатию энтера - действуем
def resize(e=None):
	c.xview_moveto((W/2.0-c.winfo_width()/2.0)/W)
	c.yview_moveto((H/2.0-c.winfo_height()/2.0)/H)
r.bind('<Configure>',resize)
Button(r,text=u'Построить',command=proc).pack(fill=X) # кнопка для того же самого
Button(r,text=u'Выйти',command=r.destroy).pack(fill=X) # кнопка выхода
# r.wm_geometry('%ix%i'%(WW_PC,HH_PC))
r.update()
for i in xrange(0,W+1,CELLSIZE): # рисование клеток и координат по вертикали
	c.create_line(i,0,i,H,fill='grey')
	c.create_text(i-3,H/2-5,text=str((i-W/2)/CELLSIZE),fill='#787878')
for i in xrange(0,H+1,CELLSIZE): # и горизонтали
	c.create_line(0,i,W,i,fill='grey')
	c.create_text(W/2+5,i,text=str((H/2-i)/CELLSIZE),fill='#787878')
c.create_line(W/2,0,W/2,H) # оси OX
c.create_line(0,H/2,W,H/2) # и OY
r.mainloop() # запуск
