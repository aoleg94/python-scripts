# -*- coding: utf-8 -*-
from Tkinter import Tk,Frame,Canvas,Scrollbar,Label,Button,Checkbutton,Entry, \
	HORIZONTAL,VERTICAL,RIGHT,LEFT,BOTH,X,Y,TOP,StringVar,IntVar
from decimal import Decimal as dec
import math,random,sys,os,time

CELLSIZE  = 96
_1_CELLSIZE = 1.0/CELLSIZE
FRAMERATE = 5*CELLSIZE
MAX_REAL=1e2 #16331239353195370.0

WW,HH=640,400 #220,230 # размеры окна
W=H=1600+2*CELLSIZE-1600%CELLSIZE # размеры поверхности

r=Tk() # создаём окно..
r.title(u'Построитель графиков функций в полярной системе координат')
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
Label(f,text='r=').pack(side=LEFT) # текстовое поле..
e=Entry(f,textvar=form)
e.pack(fill=X,side=LEFT,expand='1')
noclear=IntVar()
noclear.set(0)
Checkbutton(f,variable=noclear).pack(side=RIGHT)
f.pack(fill=X)

L=[]
FN=vars(random)
FN.update(vars(math))

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
	
def valid(y): return isinstance(y,bool) or y is None or not isinstance(y,(float,int,long))

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
	# x=px=-W*_1_CELLSIZE # начинаем рисовать за окном
	
	try:
		py=0
		px=yy=f(0)
		if abs(px)>MAX_REAL: raise ValueError
	except Exception,e:
		line=0 # если не вычисляется, то не рисуем пока
		yy=0
	errors=set()
	time=0
	from math import sin,cos,pi
	xx=0
	# while yy*CELLSIZE<max(W,H) or xx<2*pi*CELLSIZE+1:
	for xx in xrange(0,int(2*pi*CELLSIZE)): 
		x=xx*_1_CELLSIZE
		try:
			y=f(x) # вычисляем
			if isinstance(y,bool) or y is None or not isinstance(y,(float,int,long)):
				line=0
				continue
			yy=y
			x,y=y*cos(x),y*sin(x)
			if abs(y)>MAX_REAL or (yy<0 and (xx>>3)%2):
				line=0
				continue
			if line: # если предыдущая точка существует
				L.append(c.create_line((px*CELLSIZE)+W/2,(-py*CELLSIZE)+H/2,(x*CELLSIZE)+W/2,(-y*CELLSIZE)+H/2,fill=color,width=3))
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
		xx+=1
	if errors: 
		import tkMessageBox
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
for i in xrange(16):
	c.create_line(W/2,H/2,W/2+max(W,H)*math.cos(i*math.pi/8.0),H/2+max(W,H)*math.sin(i*math.pi/8.0),fill='#666666')
c.create_line(W/2,0,W/2,H) # оси OX
c.create_line(0,H/2,W,H/2) # и OY
r.mainloop() # запуск