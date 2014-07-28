import vkaptdump

if __name__=='__main__':
	import webbrowser
	while True:
		vkaptdump.check_vklogin()
		print 'http://localhost:47431/'
		webbrowser.open('http://localhost:47431/')
		try:
			vkaptdump.webview()
		except vkaptdump.ServerRestart:
			reload(vkaptdump)
			continue