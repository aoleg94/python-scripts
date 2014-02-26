# -*- coding: cp1251 -*-
from math import *
from Tkinter import *
from decimal import Decimal as dec
from random import *

def frange(start,stop,step): # генератор для дробных чисел
    start=dec(str(start))    # xrange не поддерживает float
    stop=dec(str(stop))
    step=dec(str(step))
    while start<stop:
        start+=step
        yield float(start)

W,H=480,800 # размеры поверхности
WW,HH=220,230 # размеры окна
r=Tk() # создаём окно..
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

try:
    from graphmk_f import*
except ImportError:print 'wtf'

def proc(): # здась вся соль программы
    global L
    if not noclear.get():
        for idx in L:
            c.delete(idx) # чистим поверхность от прошлого графика
        L[:]=[]
    s=form.get()
    if s=='': return # если функция не дана, то ничего не делаем
    #L.append(c.create_text(120,12,text=s))
    line=1 # флаг соединения точек (для случая x=0 в y=k/x)
    x=px=-W/16 # начинаем рисовать за окном
    try:
        py=eval(s) # вычисляем
    except:
        line=0 # если не вычисляется, то не рисуем пока
    for x in frange(-W/16,W/16,0.1): # перебор значений Х слева направо
        try:
            y=eval(s) # вычисляем
            if line: # если предыдущая точка существует
                L.append(c.create_line((px*16)+W/2,(-py*16)+H/2,(x*16)+W/2,(-y*16)+H/2,width=1))
                # то рисует линию из той в текущую точку
                r.update_idletasks() # обновляем вид, чтоб на кпк не зависало
                #print (px,py),(x,y)
            px,py=x,y # сохраняем точку
            line=1 # как существующую
        except Exception,e: # если ошибка
            line=0 # то этой точки в графике не будет
            #print e
            continue
    #print len(L)
# и так пока все точки не пройдем
e.bind('<Key-Return>',lambda x:proc()) # по нажатию энтера - действуем
#Button(r,text='process',command=proc).pack(fill=X) # кнопка для того же самого
#Button(r,text='quit',command=r.destroy).pack(fill=X) # кнопка выхода
for i in xrange(0,W+1,16): # рисование клеток и координат по вертикали
    c.create_line(i,0,i,H,fill='grey')
    c.create_text(i-3,H/2-5,text=str((i-W/2)/16),fill='#787878')
for i in xrange(0,H+1,16): # и горизонтали
    c.create_line(0,i,W,i,fill='grey')
    c.create_text(W/2+5,i,text=str((H/2-i)/16),fill='#787878')
c.create_line(W/2,0,W/2,H) # оси OX
c.create_line(0,H/2,W,H/2) # и OY
#r.protocol('WM_DELETE_WINDOW', r.quit)
#r.bind('<Destroy>',r.destroy)
r.mainloop() # запуск
#r.destroy()

