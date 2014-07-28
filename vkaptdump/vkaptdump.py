# -*- code: utf8 -*-
import vk_api
import re
import sqlite3
import time

m=re.compile(r'^(\w+)\:\s*(.*)$',re.UNICODE)
		
REGEXPS_SRC={
	'region':r'#(.*?)@(?#apartments_ekb|ekb_arenda)',
	'type':ur'(\d?(?:kk|pp|кк|рр))',
	'tel':r'(\+?[0-9() -]{10,})',
	'vk':r'(https?://vk\.com/[^ ]+)',
	'cost':r'([0-9 .,]{2,})' #r'(\d?\d[ .,]?\d{0,3})'
}

REGEXPS=dict((k,re.compile(REGEXPS_SRC[k])) for k in REGEXPS_SRC)

GID=51271270

REGION_NAMES={
	'center': u'Центр',
	'avto': u'Автовокзал',
	'akadem': u'Академический',
	'bot': u'Ботаника',
	'viz': u'Виз',
	'vokz': u'Вокзальный',
	'vtor': u'Вторчермет',
	'vtuz': u'Втузгородок',
	'eliz': u'Елизавет',
	'zhbi': u'Жби',
	'zar': u'Заречный',
	'kol': u'Кольцово',
	'comp': u'Компрессорный',
	'ns': u'Новая Сортировка',
	'park': u'Парковый',
	'pio': u'Пионерский',
	'sib': u'Сибирский тракт',
	'kamni': u'Синие камни',
	'ss': u'Старая Сортировка',
	'uktus': u'Уктус',
	'unc': u'Унц',
	'uralm': u'Уралмаш',
	'himm': u'Химмаш',
	'shart': u'Шарташ',
	'sh_ryn': u'Шарташский рынок',
	'rechka': u'Широкая речка',
	'elm': u'Эльмаш',
	'uz': u'Юго-западный',
	'ugoz': u'Юго-западный',
	'pio': u'Пионерский',
	'?': '?',
	'ugoz': u'Юго-западный',
	'pioner': u'Пионерский',
	'him': u'Химмаш',
	'ssort': u'Старая Сортировка',
	'nsort': u'Новая Сортировка',
}

REGION_POS={
	'center' : (280,305),
	'avto' : (280,385),
	'akadem' : (110,435),
	'bot' : (305,430),
	'viz' : (165,295),
	'vokz': (270,235),
	'vtor' : (250,525),
	'vtuz' : (362,286),
	'eliz' : (285,575),
	'zhbi' : (440,292),
	'zar': (205,210),
	'kol' : (810,520),
	'comp': (750,480),
	'ns' : (200,165),
	'park' : (320,335),
	'pio' : (350,225),
	'sib' : (500,360),
	'kamni' : (410,330),
	'ss' : (130,160),
	'uktus' : (365,450),
	'unc' : (175,500),
	'uralm' : (250,80),
	'himm' : (480,580),
	'shart' : (440,155),
	'sh_ryn': (340,335),
	'rechka' : (90,375),
	'elm' : (330,95),
	'uz' : (210,380),
	'ugoz' : (210,380),
	'pioner' : (350,225),
	'him' : (480,580),
	'ssort' : (130,160),
	'nsort' : (200,165),
	# '?' : (0,0)
	'pticefab' : (505,455),
	'32vg' : (217,485),
	'krasnoles' : (135,470),
}

PIXELS_TO_KM=30

def sqdist(place,home):
	if isinstance(home,basestring):
		home=REGION_POS.get(home,'?')
	if isinstance(place,basestring):
		place=REGION_POS.get(place,'?')
	if place=='?' or home=='?':return 9999999
	return (place[0]-home[0])**2+(place[1]-home[1])**2
	
def manhattan_dist(place,home):
	if place=='?' or home=='?':return '?'
	if isinstance(home,basestring):
		home=REGION_POS[home]
	if isinstance(place,basestring):
		place=REGION_POS[place]
	return (place[0]-home[0])**2+(place[1]-home[1])**2
	
def calcdisttable(home):
	if isinstance(home,basestring):
		home=REGION_POS[home]
	L=[(sqdist(p,home),p) for p in REGION_POS]
	L.sort()
	return dict((x[1],i) for i,x in enumerate(L))

class ParseError(Exception): pass

def searchpat(m,s):
	ret=m.search(s)
	if ret:
		ret=ret.groups()
		if len(ret)==1: ret=ret[0]
		return ret
	else:
		return '?'
		
def parsepost(post):
	id=post['id']
	D=parsetext(post['text'],id)
	if D is None:return D
	D['id']=id
	D['comments']=post['comments']['count']
	D['date']=post['date']
	return D

def parsetext(s,id='?'):
	try:
		s=s.replace('<br>','\n')
		L=s.split('\n')
		D={}
		lastkey=''
		for line in L[:-2]:
			g=m.match(line)
			if g:
				k,v=map(unicode.strip,g.groups())
				if k in D:
					print ' !!! "%s" already in D, post id %d'%(k,id)
				else:
					D[k]=v
				# lastkey=k
			else:
				D[lastkey]=D.get(lastkey,'')+'\n'+line
		for key in REGEXPS:
			D[key]=searchpat(REGEXPS[key],s)
		# if D.get('cost','?')=='?':
		def flt(x):
			try:
				x=int(filter(lambda c:c in '0123456789',x))
			except ValueError:
				return -9999999
			else:
				return x
		cost=searchpat(REGEXPS['cost'],D.get(u'Стоимость',(L[1:2]+[''])[0]))
		cost=max(map(flt,(D['cost'], cost)))
		D['cost']=cost if cost>0 else '?'
		D['id']=id
		D['src']=s
		D['address']=D.get(u'Адрес','?')
		D['type']=D['type'].replace(u'кк','kk').replace(u'рр','pp')
		if D['cost']=='?' or (D['address']==D['region']==D['type']=='?'):
			print ' *** http://vk.com/wall-%i_%i is not formatted'%(GID,id)
			return None
			# raise ParseError(' *** http://vk.com/wall-%i_%i is not formatted'%(GID,id))
		# else:
			# #x=int(filter(lambda c:c in '0123456789',D['cost']))
			# x=D['cost']
			# if x<1000:x*=1000
			# D['cost']=x
		# if D['type']=='?':
		if u'подселение' in s.lower() or u'койко' in s.lower():
			D['type']='pp'
		return D
	except Exception,e: 
		print ' !!! Error while parsing http://vk.com/wall-%i_%i'%(GID,id)
		raise #ParseError(e)

def dumpwall1(vk,offset=0):
	r=vk.wall.get(owner_id=-GID,count=100,offset=offset,filter='owner')
	for post in r.response[1:]:
		try:
			ret=parsepost(post)
			if ret is not None: yield ret
		except Exception,e:
			import traceback
			traceback.print_exc()
			continue

def dumpwall(vk,npages=1,cb=lambda *x:None):
	for p in xrange(npages):
		for x in dumpwall1(vk,100*p):
			yield x
		cb(p)
			
def mockup_dumpwall(*x):
	import pickle
	r=vk_api.transform(pickle.load(open('vkaptdump.pkl','rb')))
	for post in r.response[1:]:
		try:
			ret=parsepost(post)
			if ret is not None: yield ret
		except ParseError:
			import traceback
			traceback.print_exc()
			continue
			
VKLOGIN=None
def check_vklogin():
	import os
	import getpass
	global VKLOGIN
	if os.access('vkaptdump.psw',0):
		VKLOGIN=open('vkaptdump.psw','rt').read().strip('\n')
	else:
		UID=raw_input('Login: ')
		PID=getpass.getpass()
		VKLOGIN=(UID+' '+PID).strip().encode('base64')
		f=open('vkaptdump.psw','wt')
		f.write(VKLOGIN)
		f.close()
		
def vkauth():
	import getpass
	APPID=3463155
	global VKLOGIN
	if VKLOGIN is None:
		UID=raw_input('Login: ')
		PID=getpass.getpass()
	else:
		UID,PID=VKLOGIN.decode('base64').split()
	vk=vk_api.VK(UID,PID,APPID,['wall'])
	return vk	
	
def printrec(d):
	print d['src'].encode('cp866','replace'),'\n         ======>'
	for k,v in d.iteritems(): 
		if k=='src':continue
		print ('%s : %s'%(k,v)).encode('cp866','replace')
	print
	
def comparator(*fields):
	def f(a,b):
		for field in fields:
			if field[0]=='-':
				sign = -1
				field = field[1:]
			else:
				sign = 1
			if field.startswith('dist'):
				home=field.split()[1].strip()
				av=sqdist(a['region'],home)
				bv=sqdist(b['region'],home)
			else:
				av=a[field]
				bv=b[field]
			if av=='?':
				return 1
			elif bv=='?':
				return -1
			c=sign*cmp(av,bv)
			if c: return c
		return 0
	return f
	
def test():
	L=list(mockup_dumpwall())
	# for d in L:
		# print '='*55
		# printrec(d)
	import code
	intloc=locals()
	intloc.update(globals())
	code.interact(local=intloc)
	
def test_real():
	vk=vkauth()
	L=list(dumpwall(vk,int(raw_input('# pages: ') or 1)))
	dump(L)
	# for d in L:
		# print '='*55
		# printrec(d)
	import code
	intloc=locals()
	intloc.update(globals())
	code.interact(local=intloc)
	
def prepare_table():
	c=sqlite3.connect('vkaptdump.db')
	c.executescript('''
		create table if not exists posts(id integer primary key, cost integer, region text, type text, vk text, tel text, comments integer, address text, src text, edited integer, date integer);
		create table if not exists raw(id integer, key text, value text, primary key (id,key));
		delete from raw where id in (select id from posts where date<%i);
		delete from posts where date<%i;
	'''%((int(time.time()-86400*14),)*2))
	return c
	
def flatten(L):
	for x in L:
		for y in x:
			yield y
def dump(reclist):
	c=prepare_table()
	dbkeys='id cost region type vk tel comments address src date'.split()
	edited=[x[0] for x in c.execute('select id from posts where edited=1')]
	# dbposts=( tuple(rec[x] for x in dbkeys) for rec in reclist if rec['id'] not in edited)
	# dbraws=flatten( ((rec['id'],x,rec[x]) for x in rec if x not in dbkeys) for rec in reclist )
	# c.executemany('insert or replace into posts values (?,?,?,?,?,?,?,?,?,0,?)',list(dbposts))
	# c.executemany('insert or replace into raw values (?,?,?)',dbraws)
	for rec in reclist:
		if rec['id'] in edited:continue
		dbpost=tuple(rec[x] for x in dbkeys)
		dbraw=((rec['id'],x,rec[x]) for x in rec if x not in dbkeys)
		with c:
			# E=c.execute('select edited from posts where id=?',(rec['id'],)).fetchone()
			# if E is None or E[0]==0:
				c.execute('insert or replace into posts values (?,?,?,?,?,?,?,?,?,0,?)',dbpost)
				c.executemany('insert or replace into raw values (?,?,?)',dbraw)
			
def update(numpages=None,cb=lambda *x:None):
	vk=vkauth()
	L=list(dumpwall(vk,int(numpages or raw_input('# pages: ') or 1),cb))
	dump(L)
	
def fmtmainlist(c,home_region,**kw):
	yield '<table><tr><th>'+'</th><th>'.join(u'# Стоимость Район Адрес Тип Комментарии'.split())+'</th></tr>'
	import time
	cur=c.execute('select id,cost,region,type,\
	comments,address,src from posts where (type in ("kk", "?") and date>%i) order by \
		sqdist(region,?) asc, date desc, id desc, cost asc, comments asc'%int(time.time()-3600*int(kw.get("time",48))),(home_region,))
	for id,cost,region,type,\
	comments,address,src in cur:
		cost_text=c.execute('select value from raw where id=? and key=?',(id,u'Стоимость')).fetchone() or ('%i*'%cost,)
		yield '<tr><td>'+'</td><td>'.join((
			'<a href="http://vk.com/wall-%i_%i">%i</a>'%(GID,id,id),
			cost_text[0],
			REGION_NAMES.get(region,region),
			'<a href="/%s">%s</a>'%(id,address),
			type,
			str(comments)
		))+'</td></tr>'
	yield '</table>'
	
def fmteditpage(c,id):
	yield u'''<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>vkaptdump</title></head>
	<body><a href="javascript:history.back();">Назад</a> <a href="http://vk.com/wall-%i_%i">ВК</a><br>
		<form action="/%s" method="POST"><table>'''%(GID,id,id)
	K='cost region type vk tel comments address'.split()
	V=u'Стоимость Район Тип Ссылка Телефон Комментарии Адрес'.split()
	N=(1,2,3,4,5,6,7)
	D=dict(zip(N,zip(K,V)))
	X=id,cost,region,type,vk,tel,comments,address,src,edited,date=c.execute('select * from posts where id=?',(id,)).fetchone()
	for (n,(k,v)) in D.iteritems():
		yield '<tr><td>%s</td><td><input name="%s" id="%s" type="text" value="%s"></td></tr>'%(v,k,k,X[n])
	import time
	yield u'''</table><input type="submit" value="Сохранить">
		<input type="hidden" value="%s" name="id" id="id">
		<input type="hidden" value="%s" name="src" id="src">
		<input type="hidden" value="%s" name="date" id="date">
	</form><br>%s<br><i>%s</i></body></html>'''%(id,src.encode('utf8').encode('base64'),date,src,time.ctime(date))
	
class ServerRestart(RuntimeError):pass
def webview():
	import BaseHTTPServer
	import urlparse
	# update()
	c=prepare_table()
	c.create_function('sqdist',2,sqdist)
	class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		home_region='vtuz'
		def server_killer_fileno(*x):
			raise SystemExit
		def server_restarter_fileno(*x):
			raise ServerRestart
		def do_GET(self):
			self.path,qs=(self.path.rsplit('?',1)+[''])[:2]
			qs=dict(urlparse.parse_qsl(qs))
			if self.path=='/favicon.ico':
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
			elif self.path.startswith('/update'):
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
				print >>self.wfile,'updating...<br>'
				wfile=self.wfile
				def ucb(p):
					print >>wfile,'page %s done...<br>'%(p+1)
				update(int(self.path[7:] or 1),ucb)
				print >>self.wfile,'ok. <a href=/>return</a>'
			elif self.path=='/quit':
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
				print >>self.wfile,'<html><head></head><body><script>window.open("about:blank","_self").close();</script></body></html>'
				self.server.fileno=self.server_killer_fileno
			elif self.path=='/restart':
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
				# print >>self.wfile,(u'<html><head><meta http-equiv="refresh" content="%i;URL=/"></head><body>Перезапуск...<br>Если перенаправление не произойдет автоматически через %i секунд, нажмите <a href=/>сюда</a></body></html>'%((2,)*2)).encode('utf8')
				print >>self.wfile,'<html><head></head><body><script>window.open("about:blank","_self").close();</script></body></html>'
				self.server.old_fileno=self.server.fileno
				self.server.fileno=self.server_restarter_fileno
			elif self.path=='/':
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
				updhdr=u'<a href="/update">Скачать</a> <a href="/update5">Скачать 5 страниц</a> <a href="/restart">Перезапустить сервер</a> <a href="/quit">Выключить сервер</a> <a href="/?time=24">За 1 день</a> <a href="/?time=72">За 3 дня</a> <a href="/?time=168">За неделю</a><br>'#.encode('utf8')
				s=''.join(fmtmainlist(c,self.home_region,**qs)).replace('\n','<br>')
				print >>self.wfile,('''<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>vkaptdump</title><style>td:nth-child(2) { width: 20%%; } tr:nth-child(even) { background-color: #eee; }</style></head><body>%s</body></head>'''%(updhdr+s)).encode('utf8')
			else:
				self.send_response(200,'OK')
				self.send_header('Content-type','text/html')
				self.end_headers()
				s=''.join(fmteditpage(c,int(self.path[1:]))).replace('\n','<br>').encode('utf8')
				print >>self.wfile,s
		def do_POST(self):
			qs=self.rfile.read(int(self.headers['Content-Length']))
			self.send_response(200,'OK')
			self.send_header('Content-type','text/html')
			self.end_headers()
			D=dict(urlparse.parse_qsl(qs))
			# print repr(D['src'])
			D['src']=D['src'].replace('<br>','').decode('base64')
			K='id cost region type vk tel comments address src date'.split()
			c.execute('replace into posts values (?,?,?,?,?,?,?,?,?,1,?)',tuple(D[k].decode('utf8') for k in K))
			s=''.join(fmteditpage(c,int(self.path[1:]))).replace('\n','<br>').encode('utf8')
			print >>self.wfile,s
	addr=('',47431)
	server=BaseHTTPServer.HTTPServer(addr,RequestHandler)
	RequestHandler.server=server
	# while True:
	try:
		server.serve_forever()
	except ServerRestart:
		# server.fileno=
		# import os
		# os.close(server.old_fileno())
		server.socket.close()
		print
		raise
		# check_vklogin()
		# continue

	
if __name__=='__main__':
	import webbrowser
	# main(*sys.argv[1:])
	# update(1)
	check_vklogin()
	print 'http://localhost:47431/'
	webbrowser.open('http://localhost:47431/')
	webview()#test_real()