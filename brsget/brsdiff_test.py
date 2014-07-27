# -*- coding: utf8 -*-
from brsdiff import compare_fn,BRSDataError
import os,glob

def process_dir(dn):
	os.chdir(dn)
	
	old=None
	i=0
	open('diff-error.txt','w').close()
	with open('diff.txt','w') as fp:
		print >>fp,u'Отчет об изменениях в БРС:'.encode('utf8')
		for new in glob.glob('mail-*.xls'):
			print new
			# if old is None: 
				# old=new
				# continue
			i+=1
			# print 'diff-%s.txt'%i
			try:
				# with open('diff.txt','a') as fp:
					print >>fp
					print >>fp,'='*60
					print >>fp,old or '----'
					print >>fp,new
					# pos=fp.tell()
					compare_fn(fn1=old,fn2=new,fp=fp)
					# if fp.tell()==pos:
						# fp.truncate(0)
			except BRSDataError,e:
				with open('diff-error.txt','a') as fpe:
					print >>fpe
					print >>fpe,'='*60
					print >>fpe,old or '----'
					print >>fpe,new
					print >>fpe,'BRSDataError: ',e.args[0].encode('utf8')
				print >>fp,u'!! Ошибка при обработке, подробности в diff-error.txt'.encode('utf8')
			except Exception,e:
				import traceback
				with open('diff-error.txt','a') as fpe:
					print >>fpe
					print >>fpe,'='*60
					print >>fpe,old or '----'
					print >>fpe,new
					traceback.print_exc(file=fpe)
				print >>fp,u'!! Ошибка при обработке, подробности в diff-error.txt'.encode('utf8')
			old=new
	
	os.chdir('..')

def main():
	os.chdir("mail")
	for d in (x for x in os.listdir('.') if os.path.isdir(x)):
		print '='*60
		print d
		process_dir(d)

if __name__=='__main__':
	main()
