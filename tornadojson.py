# coding utf-8
'''tornado basic

'''
import json
from tornado.httpserver import HTTPServer
import tornado
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        result = {
            'abc': 'bcde'
            }
        # result = json.dumps(result)
        # self.set_header('Content-Type', 'application/json')
        self.write(result)
        
        
    def post(self, *args, **kwargs):
        self.write('响应post请求')

# create application instance
app = Application([
    ("/", IndexHandler),

])

server = HTTPServer(app)
server.listen(8888)
IOLoop.instance().start()
