import os,time

PATH=u'C:\\users\\\u041e\u043b\u0435\u0433\\Downloads'
EXT=['.'+x for x in 'jpg jpeg png gif bmp png'.split()]

os.chdir(PATH)

for fn in os.listdir('.'):
	if os.path.splitext(fn)[1].lower() not in EXT:continue
	tm=time.gmtime(os.path.getmtime(fn))
	np='images/%i-%s-%s/%s'%(tm.tm_year,str(tm.tm_mon).zfill(2),str(tm.tm_mday).zfill(2),fn)
	os.renames(fn,np)