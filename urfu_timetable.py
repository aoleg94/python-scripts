# -*- coding: utf8 -*-
import urllib2
import urllib
from urlparse import urlparse
from HTMLParser import HTMLParser

BASE_HOST="http://urfu.ru/"
BASE_URL="http://urfu.ru/student/schedule/"

class UstuScheduleParser(HTMLParser):
	@staticmethod
	def parse(url):
		f=urllib2.urlopen(url)
		s=f.read()
		f.close()
		fp=UstuScheduleParser()
		fp.feed(s)
		fp.close()
		return fp.matches
		
	def __init__(self):
		HTMLParser.__init__(self)
		self.matches={}
		self.in_div=0
		self.capture=None
		self.last=None
		self.level=0
	def handle_starttag(self, tag, attrs):
		tag = tag.lower()
		attrs=dict(attrs)
		if tag=='div':
			if "tx_ustu_schedule" in attrs.get("class",''):
				self.in_div=1
				return
			elif self.in_div==1:
				self.level+=1
		if self.in_div!=1: return
		if tag=='a':
			self.capture=''
			self.last=attrs['href']
	def handle_data(self,data):
		if self.capture is not None:
			self.capture+=data
	def handle_endtag(self,tag):
		if self.in_div!=1: return
		tag = tag.lower()
		if tag=='div':
			if self.level==0:
				self.in_div=2
			else:
				self.level-=1
			return
		if tag=='a':
			self.matches[self.capture.decode('utf8').strip()]=self.last
			self.capture=None
			self.last=None
			
def colName(classes):
	return [x.strip()[3:] for x in classes.split() if x.startswith('td-')][0]
	
COLUMNS='npair time sbname type initials aname'.split()
def rowDictToList(row):
	return tuple(row.get(k,'?') for k in COLUMNS)
			
class TimetableParser(HTMLParser):
	@staticmethod
	def parse(url):
		f=urllib2.urlopen(url)
		s=f.read()
		f.close()
		fp=TimetableParser()
		fp.feed(s)
		fp.close()
		return fp.matches
		
	def __init__(self):
		HTMLParser.__init__(self)
		self.matches={}
		self.in_div=0
		self.level=0
		self.colaccum=None
		self.last=None
		self.capture=None
		self.row=None
	def handle_starttag(self, tag, attrs):
		tag = tag.lower()
		attrs=dict(attrs)
		if tag=='div':
			if "tx_ustu_schedule" in attrs.get("class",''):
				self.in_div=1
				return
			elif self.in_div==1:
				self.level+=1
		if self.in_div!=1: return
		if tag=='h1':
			self.capture=''
			self.last=None
		elif tag=='tr':
			self.row={}
		elif tag=='td':
			name=colName(attrs['class'])
			self.row[None]=name
			self.capture=''
			if name=='npair':
				self.colaccum={}
			if 'rowspan' in attrs:
				self.colaccum[None]=name
	def handle_data(self,data):
		if self.capture is not None:
			self.capture+=data
	def handle_endtag(self,tag):
		if self.in_div!=1: return
		tag = tag.lower()
		if tag=='div':
			if self.level==0:
				self.in_div=2
			else:
				self.level-=1
			return
		if tag=='h1':
			self.matches[self.capture.decode('utf8').strip()]=self.last=[]
			self.capture=None
		elif tag=='tr':
			for key in self.colaccum:
				if key not in self.row:
					self.row[key]=self.colaccum[key]
			self.last.append(self.row)
			self.row=None
		elif tag=='td':
			name=self.row[None]
			value=self.capture.decode('utf8').strip()
			self.row[name]=value
			if None in self.colaccum:
				self.colaccum[name]=value
				del self.colaccum[None]
			self.capture=None
			del self.row[None]
			
def getFaculties():
	return UstuScheduleParser.parse(BASE_URL)
	
def getFacultyGroupList(url):
	return UstuScheduleParser.parse(url)
	
def getGroupTimetable1(url):
	return TimetableParser.parse(url)
			
def main():
	print 'Downloading faculty list'
	faculties=getFaculties()
	for name,url in faculties.iteritems():
		if u'РТФ' in name:
			print 'downloading RTF group list'
			for name,url in getFacultyGroupList(BASE_HOST+url).iteritems():
				if '220207' in name:
					print 'downloading 220207 group timetable'
					for day,rows in getGroupTimetable1(BASE_HOST+url).iteritems():
						print '====',day
						for row in rows:
							print '\t'.join(rowDictToList(row))
						
			
if __name__=="__main__":main()