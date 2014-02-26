# -*- coding: utf-8 -*-
from Tkinter import Tk,Frame,Canvas,Scrollbar,Label,Button,Checkbutton,HORIZONTAL,VERTICAL,RIGHT,LEFT,BOTH,X
from decimal import Decimal as dec
import math,random,sys,os

# def frange(start,stop,step): # генератор для дробных чисел
	# start=dec(str(start))    # xrange не поддерживает float
	# stop=dec(str(stop))
	# step=dec(str(step))
	# while start<stop:
		# start+=step
		# yield float(start)

WINMOBILE = sys.platform=='win32' and os.name=='ce'
W,H=1600,1600 # размеры поверхности
WW,HH=640,480 # размеры окна
CELLSIZE=float(16)

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
noclear=StringVar()
noclear.set('')
Checkbutton(f,onvalue='1',offvalue='',variable=noclear).pack(side=RIGHT)
f.pack(fill=X)
L=[]

# try:import graphmk_f
# except ImportError:print 'wtf'
#----------------------------------------------------------

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

	I=None
	lastx=-1e999
	def f(x):
		# global I,lastx
		if I is None or lastx>x:
			I=g([map(float,l.split()[:2]) for l in open('f.txt')])
			I.next()
		lastx=x
		return I.send(x)
	return f
	
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

def limitD(a,b,f,x):
	f=Function(f)
	if a<=x<=b:return f(x)

def limitE(a,b,f,x):
	f=Function(f)
	r=f(x)
	if a<=r<=b:return r

def clamp(a,b,f,x):
	f=Function(f)
	r=f(x)
	if r>b:return b
	elif r<a:return a
	return r
#----------------------------------------------------------

FN=vars(random)
FN.update(vars(math))
FN['prod']=prod
FN['nprod']=nprod
FN['f']=fromfile
FN['FF']=FF
FN['D']=limitD
FN['E']=limitE
FN['clamp']=clamp

def proc(): # здась вся соль программы
	global L
	if not noclear.get():
		for idx in L:
			c.delete(idx) # чистим поверхность от прошлого графика
		L[:]=[]
	s=form.get()
	if s.strip()=='': return # если функция не дана, то ничего не делаем
	#L.append(c.create_text(120,12,text=s))
	line=1 # флаг соединения точек (для случая x=0 в y=k/x)
	x=px=-W/CELLSIZE # начинаем рисовать за окном
	f=eval('lambda x:('+s+')',FN)
	try:
		py=f(x) # вычисляем
	except Exception,e:
		line=0 # если не вычисляется, то не рисуем пока
	# prevlen=len(L)
	errors=set()
	for xx in xrange(-W,W): #frange(-W/CELLSIZE,W/CELLSIZE,0.05): # перебор значений Х слева направо
		x=xx/CELLSIZE
		try:
			y=f(x) # вычисляем
			if isinstance(y,bool) or y is None or not isinstance(y,(float,int,long)):
				line=0
				continue
			# try: float(y)
			# except TypeError:
				# line=0
				# continue
			if line: # если предыдущая точка существует
				L.append(c.create_line((px*CELLSIZE)+W/2,(-py*CELLSIZE)+H/2,(xx)+W/2,(-y*CELLSIZE)+H/2,width=1))
				# то рисует линию из той в текущую точку
				r.update_idletasks() # обновляем вид, чтоб на кпк не зависало
				#print (px,py),(x,y)
			px,py=x,y # сохраняем точку
			line=1 # как существующую
		except (ArithmeticError,ValueError),e:
			line=0
			continue
		except Exception,e: # если ошибка
			line=0 # то этой точки в графике не будет
			# print e
			errors.add('%s: %s'%(e.__class__.__name__,e))
			continue
	if errors: #len(L)==prevlen and 
		import tkMessageBox
		s=u'Ошибки при вычислении:\n'
		for e in errors: s+='  %s\n'%e
		tkMessageBox.showerror(title=u'Ошибки',message=s)
	#print len(L)
# и так пока все точки не пройдем
e.bind('<Key-Return>',lambda x:proc()) # по нажатию энтера - действуем
Button(r,text=u'Построить',command=proc).pack(fill=X) # кнопка для того же самого
Button(r,text=u'Выйти',command=r.destroy).pack(fill=X) # кнопка выхода
for i in xrange(0,W+1,CELLSIZE): # рисование клеток и координат по вертикали
	c.create_line(i,0,i,H,fill='grey')
	c.create_text(i-3,H/2-5,text=str((i-W/2)/CELLSIZE),fill='#787878')
for i in xrange(0,H+1,CELLSIZE): # и горизонтали
	c.create_line(0,i,W,i,fill='grey')
	c.create_text(W/2+5,i,text=str((H/2-i)/CELLSIZE),fill='#787878')
c.create_line(W/2,0,W/2,H) # оси OX
c.create_line(0,H/2,W,H/2) # и OY
#r.protocol('WM_DELETE_WINDOW', r.quit)
#r.bind('<Destroy>',r.destroy)
r.mainloop() # запуск
#r.destroy()
