#!/usr/bin/env python
import time, os
import sqlite3 as S

#DBPATH="/var/lib/time-tracker/"
DBPATH="/home/oleg/.local/share/time-tracker/"
DBFILE=DBPATH+"db"
PERIOD=5

def pslist():
    import os
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            yield open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        except IOError: # proc has already terminated
            continue

def runs(cmd):
    return any(cmd in x for x in pslist())

def isPCUsed():
    return not runs("i3lock")

def initDB():
    if not os.access(DBPATH,0):
        os.mkdir(DBPATH)
    db = S.connect(DBFILE)
    db.executescript('''
        PRAGMA synchronous = FULL;
        create table if not exists time_tracking(date string, time integer);
    ''')
    return db

def stampDB(db):
    args = (time.strftime('%Y%m%d'), time.time())
    #print 'stamp', args
    db.execute('insert into time_tracking values (?, ?)', args)
    db.commit()

def mainloop():
    db = initDB()
    while True:
        if isPCUsed():
            stampDB(db)
        time.sleep(PERIOD)

def stat():
    db = initDB()
    print 'yyyymmdd - hh:mm:ss'
    print '-------------------'

    def finish(date, time):
        if finish.laststop is None:
            dur = PERIOD
        else:
            dur = finish.laststop - finish.laststart
        h = int(dur/3600.0)
        dur -= h*3600
        m = int(dur/60.0)
        s = int(dur - m*60)
        print "%s - %02i:%02i:%02i"%(finish.lastdate,h,m,s)
        finish.laststop = None
        finish.lastdate, finish.laststart = date, time

    finish.lastdate=None
    finish.laststart=None
    finish.laststop=None

    for date, time in db.execute('''select date, time from time_tracking order by date asc, time asc'''):
        #print 'azaz',date, time
        if finish.lastdate is None:
            finish.lastdate, finish.laststart = date, time
            finish.laststop = time + PERIOD
            continue
        if date != finish.lastdate:
            finish(date, time)
            continue
        if finish.laststop is None:
            finish.laststop = time
        if time - finish.laststop > 2*PERIOD:
            finish(date, time)
            finish.laststart = time
            finish.laststop = None
        else:
            finish.laststop = time
    finish(None, None)
    #~ for date,start,stop,dur in db.execute('''select date,min(time),max(time),max(time)-min(time) 
        #~ from time_tracking group by date;'''):
        #~ h = int(dur/3600.0)
        #~ dur -= h*3600
        #~ m = int(dur/60.0)
        #~ s = int(dur - m*60)
        #~ print "%s - %02i:%02i:%02i"%(date,h,m,s)

def stat2():
	from collections import defaultdict
	db = initDB()
	print 'yyyymmdd - hh:mm:ss'
	print '-------------------'
	D=defaultdict(list)
	for date, time in db.execute('''select date, time from time_tracking order by date asc, time asc'''):
		D[date].append(time)
	for date in D:
		dur=len(D[date])*PERIOD
		h = int(dur/3600.0)
		dur -= h*3600
		m = int(dur/60.0)
		s = int(dur - m*60)
		print "%s - %02i:%02i:%02i"%(date,h,m,s)


def main():
    import sys
    if sys.argv[1:2] in (['-d'], ['--daemon']):
        mainloop()
    if sys.argv[1:2] in (['-s'], ['--summary']):
	stat2()
    else:
        stat()

if __name__=='__main__':
    main()
