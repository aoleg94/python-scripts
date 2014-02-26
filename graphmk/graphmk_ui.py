from Tkinter import Tk,Frame,Canvas,Scrollbar,Label,Button,Checkbutton,Entry, \
	HORIZONTAL,VERTICAL,RIGHT,LEFT,BOTH,X,Y,TOP,StringVar,IntVar
	
class Window(object):
	def __init__(self,W=2432,H=1600,WW=640,HH=400,CELLSIZE=32):
		self.W,self.H,self.WW,self.HH,self.CELLSIZE=W,H,WW,HH,CELLSIZE
		self._1_CELLSIZE = 1.0/CELLSIZE
		self.FRAMERATE = 5*CELLSIZE
		self.init()
		self.L
	def init(self):
		