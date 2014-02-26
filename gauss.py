

def parse(s):
	ss=s.split('\n')
	m=len(ss[0].split())
	M=[map(lambda a:eval(a,{},{}),x.split()) for x in ss]
	for x in M:
		assert len(x)==m
	n=len(M)
	return m,n,M
	
def gcd(a, b):
	while b:
		a, b = b, a % b
	return a

def gcd2(*a):
	return reduce(gcd,a)
	
def lcm(a,b):
	return abs(a*b)/gcd(a,b)
	
# def sanitize(M):
	# for x in M[:]:
		# if not any(x):M.remove(x)
	# for a 
	# return len(M[0]),len(M)
	
def sumrows(M,i,j,n,out):
	if n>=len(M[0]):
		return
	if M[i][n]<0:
		for x in xrange(len(M[i])): M[i][x]=-M[i][x]
		out(M)
	a=M[i][n]
	b=M[j][n]
	try:
		l=lcm(a,b)
		c=-l/a
		d= l/b
	except ZeroDivisionError: return
	if b<0:c=-c;d=-d
	for x in xrange(len(M[i])): M[j][x]=c*M[i][x]+d*M[j][x]
	out(M)
	
def prm(M):
	if isinstance(M,str):print M
	else:
		for x in M:
			for y in x:
				print '%6g'%y,
			print
		print '-'*40

def solve(m,n,S,out):
	M=[[y for y in x] for x in S]
	def sort(M,rev=0):
		B=M[:]
		M.sort(reverse=not rev)
		if B!=M: out(M)
	out(M)
	sort(M,1)
	for i in xrange(m-1):
		for j in xrange(i+1,n):
			sumrows(M,i,j,i,out)
		sort(M)
	for i in xrange(n-1,0,-1):
		for j in xrange(i-1,-1,-1):
			sumrows(M,i,j,i,out)
		sort(M)
	sort(M)
	for j in xrange(n):
		g=gcd2(*M[j])
		if g:
			for i in xrange(m):
				M[j][i]/=g
		s=0
		for i in xrange(m):
			if M[j][i]==0:continue
			if s==0:
				if M[j][i]<0:s=-1
				else:s=1 
			M[j][i]*=s
	sort(M)
	out(M)
	# return M
	