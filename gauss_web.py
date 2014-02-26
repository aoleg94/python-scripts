# -*- coding: utf8 -*-
import gauss
import BaseHTTPServer
from urllib import quote,unquote

FRONTPAGE='''<html><head><title>Решение СЛУ методом Гаусса</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <script type="text/javascript" src="jquery.min.js"></script></head><body>
	<textarea id="req" style="width: 90%; height: 35%"></textarea>
	<input type="submit" value="Send" style="float: right;" id="btn"><br>
	<pre id="out"></pre><br>
	<script>
		$(function(){
			var out = $('#out')[0];
			var btn = $('#btn');
			var req = $('#req')[0];
			btn.click(function(){
				var sql = req.value;
				while(sql.indexOf('\\n')!=-1) 
					sql = sql.replace('\\n','lf');
				$.get("/"+sql,function(data){
					out.innerText=data+'\\n\\n';
					//req.value="";
					window.scrollTo(0,document.height);
				});
			});
		});
	</script>
</body></html>'''

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path=='/':
			reload(gauss)
			self.send_response(200,'OK')
			self.send_header('Content-type','text/html')
			self.end_headers()
			print >>self.wfile,FRONTPAGE
		elif self.path=='/jquery.min.js':
			self.send_response(200,'OK')
			self.send_header('Content-type','text/html')
			self.end_headers()
			with open('jquery.min.js') as f:
				print >>self.wfile,f.read()
		elif self.path=='/favicon.ico':
			self.send_response(404)
		else:
			data=unquote(self.path[1:]).replace('lf','\n').strip()
			# print data
			self.send_response(200,'OK')
			self.send_header('Content-type','text/html')
			self.end_headers()
			try:
				m,n,M=gauss.parse(data)
				def outf(M):
					if isinstance(M,str):print >>self.wfile,M
					else:
						for x in M:
							for y in x:
								print >>self.wfile,'%6s'%y,
							print >>self.wfile
						print >>self.wfile,'-'*40
				gauss.solve(m,n,M,outf)
			except Exception,e:
				import traceback
				print >>self.wfile,traceback.format_exc()
			
def main():
	addr=('',64755)
	server=BaseHTTPServer.HTTPServer(addr,RequestHandler)
	server.serve_forever()
if __name__=='__main__':main()