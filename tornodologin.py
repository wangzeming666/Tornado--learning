# coding utf-8
'''tornado basic

'''

from tornado.httpserver import HTTPServer
import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('hello, world')
    def post(self, *args, **kwargs):
        self.write('响应post请求')

# create application instance
app = Application([
    ("/", IndexHandler),

], template_path=os.path.join(os.path.dirname(__file__), "templates"),)

server = HTTPServer(app)
server.listen(8888)
IOLoop.instance().start()
