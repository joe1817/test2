import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class SPAHandler(SimpleHTTPRequestHandler):
	def do_GET(self):
		# Strip the /test2 prefix if present so Python can find the local files
		if self.path.startswith('/test2'):
			self.path = self.path[len('/test2'):]
			if not self.path:
				self.path = '/'

		# If the requested path doesn't point to a real file or directory,
		# fall back to index.html to let Vue Router handle the route.
		path_translated = self.translate_path(self.path)
		if not os.path.exists(path_translated) or os.path.isdir(path_translated):
			# Check if it's a request for a static asset (like css, js, json)
			if '.' in self.path.split('/')[-1] and not self.path.endswith('/'):
				self.send_error(404, "File not found")
				return
			self.path = '/index.html'

		return super().do_GET()

if __name__ == '__main__':
	os.chdir('docs')
	server_address = ('localhost', 8000)
	print("Serving on http://localhost:8000/test2/")
	httpd = HTTPServer(server_address, SPAHandler)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print("\nServer stopped.")