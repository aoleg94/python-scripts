#!/usr/bin/env python
import time, os
import sqlite3 as S

#DBPATH="/var/lib/time-tracker/"
DBPATH="/home/oleg/.local/share/time-tracker/"
DBFILE=DBPATH+"db"
PERIOD=5
SALARY_PER_HOUR_DEFAULT=120
SALARY_DAY=10

def pslist():
    import os
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            yield open(os.path.join('/proc', pid, 'cmdline'), 
                'rb').read()
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
        create table if not exists 
            time_tracking(date string, time integer);
    ''')
    return db

def stampDB(db):
    args = (time.strftime('%Y%m%d'), int(time.time()))
    #print 'stamp', args
    db.execute('insert into time_tracking values (?, ?)', args)
    db.commit()

def mainloop():
    db = initDB()
    while True:
        if isPCUsed():
            stampDB(db)
        time.sleep(PERIOD)

def hms(dur):
    h = int(dur/3600.0)
    dur -= h*3600
    m = int(dur/60.0)
    s = int(dur - m*60)
    return h,m,s

def stat():
    db = initDB()
    print 'yyyymmdd - hh:mm:ss'
    print '-------------------'

    def finish(date, time):
        if finish.laststop is None:
            dur = PERIOD
        else:
            dur = finish.laststop - finish.laststart
        print "%s - %02i:%02i:%02i"%((finish.lastdate,)+hms(dur))
        finish.laststop = None
        finish.lastdate, finish.laststart = date, time

    finish.lastdate=None
    finish.laststart=None
    finish.laststop=None

    for date, time in db.execute('''
        select date, time from time_tracking 
            order by date asc, time asc'''):
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

def stat2():
    from collections import defaultdict
    db = initDB()
    print 'yyyymmdd - hh:mm:ss'
    print '-------------------'
    D=defaultdict(list)
    for date, time in db.execute('''
        select date, time from time_tracking 
            order by date asc, time asc'''):
        D[date].append(time)
    for date in sorted(D):
        dur = len(D[date])*PERIOD
        print "%s - %02i:%02i:%02i"%((date,)+hms(dur))

def statm(yearmonth=None,salary_per_hour=SALARY_PER_HOUR_DEFAULT):
    from collections import defaultdict
    import time
    db = initDB()
    print 'yyyymmdd - hh:mm:ss - salary'
    print '----------------------------'
    D=defaultdict(list)
    salary_per_hour = int(salary_per_hour)
    if yearmonth is None:
        tm = time.localtime()
        y = tm.tm_year
        m = tm.tm_mon
        if tm.tm_mday < SALARY_DAY:
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        yearmonth = (y, m)
    elif len(yearmonth) <= 2:
        tm = time.localtime()
        yearmonth = (tm.tm_year, int(yearmonth))
    elif len(yearmonth) <= 6:
        yearmonth = (int(yearmonth[:4]), int(yearmonth[4:]))
    daterange = (
        time.mktime(
            (yearmonth[0], yearmonth[1]+0, SALARY_DAY, 0,0,0, 0,0,-1)),
        time.mktime(
            (yearmonth[0], yearmonth[1]+1, SALARY_DAY, 0,0,0, 0,0,-1)))
    for date, time in db.execute('''
        select date, time from time_tracking 
            where time between ? and ? 
            order by date asc, time asc''', daterange):
        D[date].append(time)
    dur_sum = 0
    for date in sorted(D):
        dur = len(D[date])*PERIOD
        dur_sum += dur
        salary = dur/3600.0 * salary_per_hour
        print "%s - %02i:%02i:%02i - %6i"%((date,)+hms(dur)+(salary,))
    print '----------------------------'
    dur = dur_sum
    salary = dur/3600.0 * salary_per_hour
    print "%04i%02i__ - %02i:%02i:%02i - %6i"%(
        yearmonth+hms(dur)+(salary,))

def schedule(lastN="31"):
    db = initDB()
    lastN = int(lastN)
    print 'yyyymmdd - hh:mm:ss - hh:mm:ss - hh:mm:ss'
    print '-----------------------------------------'
    for date, mintime, maxtime, count in db.execute('''
        select * from (select date, min(time), max(time), count(time) 
            from time_tracking group by date 
            order by date desc limit ?) order by date asc''', (lastN,)):
        mintime = (mintime - time.timezone) % 86400
        maxtime = (maxtime - time.timezone) % 86400
        print "%s - %02i:%02i:%02i - %02i:%02i:%02i - %02i:%02i:%02i"%(
            (date,)+hms(mintime)+hms(maxtime)+hms(count*PERIOD))
    print '-----------------------------------------'
    mintime, maxtime, count = [], [], []
    for mi, ma, co in db.execute('''
        select min(time) as mi, max(time) as ma, count(time) as co
            from time_tracking group by date 
            order by date desc limit ?''', (lastN,)):
        mintime.append(mi); maxtime.append(ma); count.append(co)
    mintime, maxtime = map(lambda L: sum((x - time.timezone)%86400 for x in L)/len(L) if L else 0, (mintime, maxtime))
    count = sum(count)/len(count) if count else 0
    print "     avg - %02i:%02i:%02i - %02i:%02i:%02i - %02i:%02i:%02i"%(
        hms(mintime)+hms(maxtime)+hms(count*PERIOD))

def main():
    import sys
    if sys.argv[1:2] in (['-d'], ['--daemon']):
        mainloop()
    elif sys.argv[1:2] in (['-f'], ['--full']):
        stat()
    elif sys.argv[1:2] in (['-m'], ['--month']): # -m {2|02|201602} {salary per hour}
        statm(*sys.argv[2:4]) # echo `time-tracker -m | tail -n3 | tr -d ' ' | cut -d- -f2,3 --output-delimiter=' ' | sed -e 's/^ $/|/' `
    elif sys.argv[1:2] in (['-s'], ['--schedule']):
        schedule(*sys.argv[2:3])
    else:
        stat2()

if __name__=='__main__':
    main()
