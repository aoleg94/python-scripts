# -*- coding: utf-8 -*-
import xlrd
import re

_types={
	'str':unicode,
	'int':int,
	'float':float
}
def checktype(o,t):
	if t[0]=='{':
		return isinstance(o,dict) and all(checktype(x,t[1:]) for x in o.itervalues())
	if t[0]=='[':
		return isinstance(o,list) and all(checktype(x,t[1:]) for x in o)
		# return isinstance(o,TypedList) and o.type==t[1:] and o.check()
	if not iscompound(t):
		try:
			o=_types.get(t)(o)
		except Exception:pass
	return isinstance(o,_types.get(t,()))
	
def getdefault(t):
	# print 1,
	if t[0]=='[': return [] # TypedList(t[1:])
	if t[0]=='{': return {} # TypedList(t[1:])
	assert t in _types,'Unknown type'
	# if not hasattr(_types.get(t,None),'_compound'):
	return _types[t]()
	assert False
	
def iscompound(t):
	return hasattr(_types.get(t,None),'_compound') or t[0] in '[{'

class TypedList(list):
	def __init__(self,type,data=None):
		self.data=data if data is not None else []
		self.type=type
		self.check()
	def check(self):
		assert all(checktype(x,self,type) for x in self.data),'Type consistence has been violated'
		return True
	def __getattribute__(self,n):
		if n in ('data','type','check'):
			return object.__getattr__(self,n)
		f=getattr(self.data,n)
		if callable(f):
			def g(self,*x):
				v=f(self.data,*x)
				if isinstance(v,TypedList):
					return TypedList(self.type,v)
				self.check()
				return v
			return g
		if n.startswith('__'): return f
	def __str__(self):
		return 'TypedList(%s, %s)'%(self.type,self.data)
	__repr__=__str__

def mktype(name,s):
	class a(object):
		_compound=1
		_fields=dict(x.strip().split('/',1) for x in s.split() if x.strip())
		__doc__='%s(%s)'%(name,', '.join(_fields))
		__name__=name
		_values=None
		def __init__(self,**kw):
			self._values={}
			for f,t in self._fields.iteritems():
				key=f
				value=kw.get(f,None)
				if value is None or value=='':
					value=getdefault(t)
				setattr(self,key,value)
				# assert checktype(value,t)
				# self._values[key]=value
		def __getattr__(self,a):
			v=self._values[a]
			assert checktype(v,self._fields[a])
			return v
		def __setattr__(self,a,v):
			if a=='_values':
				object.__setattr__(self,a,v)
				return
			if not iscompound(self._fields[a]):
				v=_types[self._fields[a]](v)
			assert checktype(v,self._fields[a])
			self._values[a]=v
		def __repr__(self):
			return '<%s>'%str(self)
		def __str__(self):
			return '%s(%s)'%(self.__name__,', '.join( '%s=%r'%(kv) for (kv) in self._values.iteritems()))
		def __eq__(self,o):
			return self._values==getattr(o,'_values',None)
	a.__name__=name
	_types[name]=a
	return a
			
Subject=mktype('Subject','name/str semester/str year/str student/str pts/float mark/str sections/{Section')
Section=mktype('Section','name/str coef/float teacher/str works/[Work exam/Work examcoef/float')
Work=mktype('Work','name/str pts/float max/int')

m=re.compile(r'(?:(.*?)(?:\((.*)\))? ([.0-9]+))',re.U)

def parseSubjectList(sh):
	semname=sh.cell_value(2,1)
	i=3 # 4th
	while True:
		name=sh.cell_value(i,2)
		if name:
			pts=sh.cell_value(i,3)
			mark=sh.cell_value(i,4)
			yield (0,name,pts,mark)
		else:
			break
		i+=1
	i+=1
	while True:
		name=sh.cell_value(i,2)
		if name:
			pts=sh.cell_value(i,3)
			mark=sh.cell_value(i,4)
			yield (1,name,pts,mark)
		else:
			break
			
			
def parseSection(sh,row,sections):
	name,teacher=sh.cell_value(row,0).split('(')
	name=name.strip().lower()
	teacher=teacher[:-1].strip()
	section=sections.get(name, Section(name=name, coef=0.0))
	section.teacher=teacher
	
	column=0
	while True:
		title=sh.cell_value(row+3,column)
		if '=' not in title: break
		wname,max=map(unicode.strip, title.rsplit('=',1))
		pts=sh.cell_value(row+4,column)
		section.works.append(Work(name=wname,pts=pts,max=max))
		column+=1
		
	title=sh.cell_value(row+8,0)
	_,_,examcoef=m.match(title).groups()
	if examcoef!='1.0':
		title=sh.cell_value(row+8,1)
		assert '=' in title
		wname,max=map(unicode.strip, title.rsplit('=',1))
		pts=sh.cell_value(row+9,1)
		section.exam=Work(name=wname,pts=pts,max=max)
		section.examcoef=1.0-float(examcoef)
		
def parseSubject(sh):
	student=sh.cell_value(0,0)
	subjname,semname,yearstr=map(unicode.strip,sh.cell_value(1,0).split('.'))
	subj=Subject(name=subjname.capitalize()+' (%s)'%semname,semester=semname,year=yearstr,student=student)
	i=0
	while True:
		g=m.match(sh.cell_value(4,i))
		if not g:break
		title,name,coef=g.groups()
		assert name and coef
		subj.sections[name]=Section(name=name,coef=coef)
		i+=1
	if sh.cell_value(5,i+2):
		i+=2
	try:
		subj.pts=sh.cell_value(5,i)
	except Exception:
		subj.pts=0.0
	subj.mark=sh.cell_value(5,i+1)
	
	row = 8
	while row < sh.nrows and sh.cell_value(row,0):
		parseSection(sh,row,subj.sections)
		row+=12
	return subj
	
def printSubject(subj,fp=None):
	print >>fp,u'Предмет:',subj.name
	print >>fp,u'Семестр:',subj.semester
	print >>fp,u'Год:',subj.year
	print >>fp,u'Итоговый балл:',subj.pts
	print >>fp,u'Оценка:',subj.mark
	print >>fp,u'Разделы:'
	for sec in subj.sections.itervalues():
		print >>fp,u' - '+sec.name.capitalize()+':'
		print >>fp,u'     Коэффициент раздела:',sec.coef
		print >>fp,u'     Преподаватель:',sec.teacher
		if sec.exam.max:
			print >>fp,u'    ',u'%s (%.1f):'%(sec.exam.name.capitalize(),sec.examcoef),'%.0f/%i'%(sec.exam.pts,sec.exam.max)
		print >>fp,u'     Работы (%.1f):'%(1.0-sec.examcoef)
		for w in sec.works:
			print >>fp,u'       ',w.name+u':','%.0f/%i'%(w.pts,w.max)
			
def printSubjects(subj_seq,fp):
	for subj in subj_seq:
		print >>fp,'='*40
		printSubject(subj,fp)

def parseXLS(fn):
	wb=xlrd.open_workbook(fn)
	# sh=wb.sheet_by_index(0)
	# assert sh.name==u'Дисциплины'
	# subjs=parseSubjectList(sh)
	for sh in wb.sheets()[1:]:
		yield parseSubject(sh)
		
def main():
	import sys
	fn=(sys.argv[1:2]+['brs-1-1.xls'])[0]
	it=parseXLS(fn)
	# print it.next()
	import codecs
	f=codecs.getwriter(sys.stdout.encoding or 'cp866')(sys.stdout)
	f.errors='ignore'
	printSubjects(it,f)
if __name__=='__main__':main()
