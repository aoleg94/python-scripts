# -*- coding: utf8 -*-
from random import randint,choice

hex1=__builtins__.hex
oct1=__builtins__.oct
bin1=__builtins__.bin

def hex(n):
	if n<0: return '-'+hex(-n)
	return hex1(n)[2:]+'(16)'

def bin(n):
	if n<0: return '-'+bin(-n)
	return bin1(n)[2:]+'(2)'

def oct(n):
	if n<0: return '-'+oct(-n)
	return oct1(n)[1:]+'(8)'
	
def fract_10_2(x,d=10):
	if x<0:return '-'+fract_10_2(-x,d)
	intpart=int(x)
	x-=intpart
	n=0
	s=bin1(intpart)[2:]+'.'
	while x and n<d:
		x*=2
		if x>=1:
			s+='1'
			x-=1
		else:
			s+='0'
		n+=1
	if n==d:s+='...'
	if n==0:s+='0'
	return s
		
	
numlen={2: 2**8, 8: 8**4, 10: 400, 16: 16**5}
funcs={2: bin, 8: oct, 10: (lambda n:'%i(10)'%n), 16: hex}
	
def test_int():
	bases=(2,8,10,16)
	b1=choice(bases)
	b2=choice([x for x in bases if x!=b1])
	# assert b1 in (2,8,10,16), u'основание системы счисления должно быть 2,8,10 или 16'
	# assert b2 in (2,8,10,16), u'основание системы счисления должно быть 2,8,10 или 16'
	
	x=randint(1,numlen[b1])
	print funcs[b1](x),'= ?(%i)'%b2
	try:
		i=int(raw_input('? = '),b2)
	except ValueError:
		i=None
	if i==x: print u' -> Верно'
	else: print u' -> Неверно, правильный ответ %s'%funcs[b2](x)
	
def test_fract():
	l=randint(3,6)
	x=randint(0,90)+(randint(1,2**l-1)/(2.0**l))
	print '%.10g(10) = ?(2)'%x
	s=raw_input('? = ')
	if s==fract_10_2(x): print u' -> Верно'
	else: print u' -> Неверно, правильный ответ %s'%fract_10_2(x)
		
		
numlen2={2: 6, 8: 2, 16: 2}
def test_fract2(d=10):
	bases=(2,8,16)
	b=choice(bases)
	
	l=randint(1,numlen2[b])
	s=funcs[b](randint(1,numlen[b]+l))[:-len('(%i)'%b)]
	i,f=s[:-l],s[-l:]
	if not i:i='0'
	if not f:f='0'
	i10=int(i,b)
	f10=int(f,b)/float(b)**l
	assert f10 < 1
	f10s=str(int(f10*10.0**d)/10.0**d)[2:]
	s10='%s.%s'%(i10,f10s)
	
	print '%s.%s(%i) = ?(10)'%(i,f,b)
	x=raw_input('? = ')
	if s10==x: print u' -> Верно'
	else: print u' -> Неверно, правильный ответ %s'%s10
	
def main():
	print u'''Чем занимаемся?
	1. Целые
	2. Дробные (10->2)
	3. Дробные ({2,8,16}->10)
	(Enter) - все тесты
	
> ''',
		
	tests=[test_int,test_fract,test_fract2]
	assert len(tests)<10
	cc=raw_input().strip().replace(' ','') or ''.join(str(x+1) for x in xrange(len(tests)))
	while True:
		c=int(choice(cc),16)-1
		try:
			tests[c]()
		except Exception: 
			print u'Произошла ошибка'
			raise
		print u'[Enter - еще раз, <любая кнопка>+Enter - завершить]',
		if raw_input(): break
		
	
if __name__=='__main__':main()