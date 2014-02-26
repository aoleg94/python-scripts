# -*- coding: cp1251 -*-
from distutils.core import setup
import py2exe
import os
import time

kw=dict(
	name="Graphmk",
	version='1.0',
	windows=['graphmk.pyw'],
	#zipfile=None,
	options={
		"py2exe": {
			'optimize':1,
			'excludes':['pydoc','socket'],
			'dist_dir':'bin',
			'compressed':False,
			'bundle_files':3
		}
	}
)

setup(**kw)

os.chdir('bin')
os.system('upx --ultra-brute *')
os.system('7z u graphmk.7z * -mx=9 -ms=on -x!graphmk.7z')