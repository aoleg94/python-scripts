from brsget import clearcfg,putcfg,loadcfg,process,getcfg
from brsparse import parseXLS,Subject,Section,Work,printSubject

# Subject=mktype('Subject','name/str semester/str year/str pts/float mark/str sections/{Section')
# Section=mktype('Section','name/str coef/float teacher/str works/[Work exam/Work examcoef/float')
# Work=mktype('Work','name/str pts/float max/int')

class BRSDataError(RuntimeError):pass

class BRSDiffOutputBase(object):
	def writeSubject(self,subj,action):
		raise NotImplementedError
	def writeSection(self,subj,section,action):
		raise NotImplementedError
	def writeWork(self,subj,section,work,action):
		raise NotImplementedError

class BRSDiffOutputCallLogger(object):
	def __getattr__(self,n):
		def f(*a):
			print '%s%s'%(n,a)
		return f
		
def prepend_call(f1):
	def r(f2):
		def r2(*a):
			f1(*a)
			return f2(*a)
		return r2
	return r
class BRSDiffOutputConsoleLogger(BRSDiffOutputBase):
	def __init__(self,fp=None,encoding=None):
		import codecs,sys
		f=fp or sys.stdout
		fp=codecs.getwriter(encoding or getattr(f,'encoding',None) or 'cp866')(fp or sys.stdout)
		fp.errors='ignore'
		self.f=fp
		self._hierarchy=[None,None,None]
	SYMBOLS={
		'add':'+',
		'del':'-',
		'mod':'*',
		'inc':'^',
		'dec':'v'
	}
	def enforceHierarchy(self,*a):
		action=a[-1]
		a=list(a[:-1])+[None,None,None,None]
		h=subj,section,work,dummy=a[:4]
		lvl=h.index(None)-1
		for i in xrange(lvl):
			if h[i]!=self._hierarchy[i]:
				self.HIERARCHY_FUNCS[i](self,*(h[:i+1]+['mod']))
		self._hierarchy=h
	@prepend_call(enforceHierarchy)
	def writeSubject(self,subj,action):
		# self.enforceHierarchy(subj,action)
		print >>self.f,'%s %s (%g %s)'%(self.SYMBOLS[action],subj.name,subj.pts,subj.mark)
		# printSubject(subj,self.f)
		# if action=='mod':
			# print >>self.f,'pts=%g, mark=%s'%(subj.pts,subj.mark)
	@prepend_call(enforceHierarchy)
	def writeSection(self,subj,section,action):
		# self.enforceHierarchy(subj,section,action)
		# print >>self.f,'section %s: %s(%s,%s) \n\tin subject "%s"'%(action,section.name,section.coef,section.examcoef,subj.name)
		print >>self.f,'  %s %s(%s,%s)'%(self.SYMBOLS[action],section.name,section.coef,section.examcoef)
		# print >>self.f,'coef=%s, examcoef=%s'%(section.coef,section.examcoef)
	@prepend_call(enforceHierarchy)
	def writeWork(self,subj,section,work,action):
		# self.enforceHierarchy(subj,section,work,action)
		print >>self.f,'    %s %s (%g/%s)'%(self.SYMBOLS[action],work.name,work.pts,work.max)
		# print >>self.f,'work %s: %s (%g/%s)\n\tin section "%s" \n\tin subject "%s"'%(action,work.name,work.pts,work.max,section.name,subj.name)
		# print >>self.f,'pts=%g, max=%s'%(work.pts,work.max)
	HIERARCHY_FUNCS=[writeSubject,writeSection,writeWork]

@apply		
class nonmatchy(object):
	def __getattr__(self,n):
		return self
	def __eq__(self,o):
		return False
		
def split(s):
	if isinstance(s,list):
		return s
	return s.split()
	
def compare(old,new,properties):
	properties=split(properties)
	diff={}
	for n in properties:
		ov=getattr(old,n)
		nv=getattr(new,n)
		if ov!=nv:
			diff[n]=(ov,nv)
	return diff
	
def compare_act(old,new,n):
	ov=getattr(old,n)
	nv=getattr(new,n)
	if ov is nonmatchy:
		return "mod"
	if nv<ov:
		return "dec"
	elif nv>ov:
		return "inc"
	else:
		return "mod"
	
	
def mkdict(seq):
	if isinstance(seq,dict):
		return seq
	D={}
	for x in seq:
		suffixn=0
		suffix=''
		name=x.name
		k=name
		while k in D:
			suffixn+=1
			suffix=' [%i]'%suffixn
			k=name+suffix
		D[k]=x
	return D

def checkattr(old,new,properties):
	properties=split(properties)
	if old is nonmatchy:
		return
	diff=compare(old,new,properties)
	if diff:
		# o=tuple(getattr(old,n) for n in properties)
		# n=tuple(getattr(new,n) for n in properties)
		# template="(%s)"%(','.join(["%s"]*len(properties)))
		msg="data mismatch:"
		diff['name']=(old.name,new.name)
		for pname in diff:
			o,n=diff[pname]
			msg+=u"\n\told.%s = %s\n\tnew.%s = %s"%(pname,o,pname,n)
		# raise BRSDataError,(("data mismatch: %s vs %s")%(template,template))%(o+n)
		raise BRSDataError,msg
		
def checklist(old,new,attr,ff,prepend):
	old=getattr(old,attr) if old is not nonmatchy else []
	new=getattr(new,attr)
	od=mkdict(old)
	nd=mkdict(new)
	o=set(od)
	n=set(nd)
	i=n.intersection(o)
	if len(o)>0 and len(i)==0:
		raise BRSDataError,"%s list mismatch in '%s', wtf"%(attr,new.name)
	prepend=(tuple(prepend) if isinstance(prepend,(tuple,list)) else (prepend,))
	f=lambda x,a:ff(*(prepend+(x,a)))
	for x in o.difference(n):
		f(od[x],'del')
	for x in n.difference(o):
		f(nd[x],'add')
	return ((od.get(s,nonmatchy),nd[s]) for s in sorted(i))
	
def diffWorks(subj,sec,old,new,out):
	checkattr(old,new,'name')
	if compare(old,new,'pts max'):
		out.writeWork(subj,sec,new,compare_act(old,new,'pts'))
	
		
def diffSections(subj,old,new,out):
	checkattr(old,new,'name')
	if old is not nonmatchy and compare(old,new,'teacher coef examcoef'):
		out.writeSection(subj,new,"mod")
	sec=new
	i=checklist(old,new,'works',out.writeWork,(subj,sec))
	for o,n in i:
		diffWorks(subj,sec,o,n,out)
	diffWorks(subj,sec,old.exam,new.exam,out)

def diffSubjects(old,new,out):
	checkattr(old,new,'name semester year')
	if old is not nonmatchy and compare(old,new,'pts mark'):
		out.writeSubject(new,compare_act(old,new,'pts'))
	#
	subj=new
	i=checklist(old,new,'sections',out.writeSection,subj)
	for o,n in i:
		diffSections(subj,o,n,out)

def diffSubjectList(old,new,out):
	od=mkdict(old)
	nd=mkdict(new)
	o=set(od)
	n=set(nd)
	i=n.intersection(o)
	if len(o)>0 and len(i)==0:
		raise BRSDataError,"subject list mismatch, probably wrong file"
	for subj in sorted(o.difference(n)):
		out.writeSubject(od[subj],'del')
	for subj in sorted(n.difference(o)):
		out.writeSubject(nd[subj],'add')
		diffSubjects(nonmatchy,nd[subj],out)
		# checklist(nonmatchy,nd[subj],'sections',out.writeSection,nd[subj])
	for s in sorted(i):
		diffSubjects(od.get(s,nonmatchy),nd[s],out)

def process_diff(cfg=None,brs_user=None,brs_password=None):
	import os
	loadcfg(cfg or "brsdiff.cfg")
	if brs_user is not None:
		putcfg("User",brs_user)
	if brs_password is not None:
		putcfg("Password",brs_password)
	putcfg("File mask","brs-new-%s.xls")
	process()
	fn1="brs-old-1.xls"
	if not os.access(fn1):
		fn1=None
	compare_fn(fn1=fn1,fn2="brs-new-1.xls",fp="brsdiff.txt")
	os.rename("brs-new-1.xls","brs-old-1.xls")
	
def compare_fn(fn2="2.xls",fn1="1.xls",fp=None):
	out=BRSDiffOutputConsoleLogger(fp,'cp866' if fp is None else 'utf8')
	it1=parseXLS(fn1) if fn1 is not None else []
	it2=parseXLS(fn2)
	diffSubjectList(it1,it2,out)

if __name__=='__main__':
	# main()
	import sys
	# compare_fn(*sys.argv[1:3])
	process_diff("brsget-1.cfg")