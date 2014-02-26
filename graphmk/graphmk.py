# -*- coding: cp1251 -*-
from math import *
from Tkinter import *
from decimal import Decimal as dec
from random import *

def frange(start,stop,step): # ��������� ��� ������� �����
    start=dec(str(start))    # xrange �� ������������ float
    stop=dec(str(stop))
    step=dec(str(step))
    while start<stop:
        start+=step
        yield float(start)

W,H=480,800 # ������� �����������
WW,HH=220,230 # ������� ����
r=Tk() # ������ ����..
f=Frame() # �����..
c=Canvas(f,width=WW,height=HH,bg='white',scrollregion=(0,0,W,H)) # �����������..
sX=Scrollbar(r,orient=HORIZONTAL) # ����������
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
Label(f,text='y=').pack(side=LEFT) # ��������� ����..
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

def proc(): # ����� ��� ���� ���������
    global L
    if not noclear.get():
        for idx in L:
            c.delete(idx) # ������ ����������� �� �������� �������
        L[:]=[]
    s=form.get()
    if s=='': return # ���� ������� �� ����, �� ������ �� ������
    #L.append(c.create_text(120,12,text=s))
    line=1 # ���� ���������� ����� (��� ������ x=0 � y=k/x)
    x=px=-W/16 # �������� �������� �� �����
    try:
        py=eval(s) # ���������
    except:
        line=0 # ���� �� �����������, �� �� ������ ����
    for x in frange(-W/16,W/16,0.1): # ������� �������� � ����� �������
        try:
            y=eval(s) # ���������
            if line: # ���� ���������� ����� ����������
                L.append(c.create_line((px*16)+W/2,(-py*16)+H/2,(x*16)+W/2,(-y*16)+H/2,width=1))
                # �� ������ ����� �� ��� � ������� �����
                r.update_idletasks() # ��������� ���, ���� �� ��� �� ��������
                #print (px,py),(x,y)
            px,py=x,y # ��������� �����
            line=1 # ��� ������������
        except Exception,e: # ���� ������
            line=0 # �� ���� ����� � ������� �� �����
            #print e
            continue
    #print len(L)
# � ��� ���� ��� ����� �� �������
e.bind('<Key-Return>',lambda x:proc()) # �� ������� ������ - ���������
#Button(r,text='process',command=proc).pack(fill=X) # ������ ��� ���� �� ������
#Button(r,text='quit',command=r.destroy).pack(fill=X) # ������ ������
for i in xrange(0,W+1,16): # ��������� ������ � ��������� �� ���������
    c.create_line(i,0,i,H,fill='grey')
    c.create_text(i-3,H/2-5,text=str((i-W/2)/16),fill='#787878')
for i in xrange(0,H+1,16): # � �����������
    c.create_line(0,i,W,i,fill='grey')
    c.create_text(W/2+5,i,text=str((H/2-i)/16),fill='#787878')
c.create_line(W/2,0,W/2,H) # ��� OX
c.create_line(0,H/2,W,H/2) # � OY
#r.protocol('WM_DELETE_WINDOW', r.quit)
#r.bind('<Destroy>',r.destroy)
r.mainloop() # ������
#r.destroy()

