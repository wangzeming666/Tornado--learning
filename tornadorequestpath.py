import tornado
from tornado.web import Application, RequestHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define,options,parse_config_file
import os

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write("hello")

    def post(self, *args, **kwargs):
        query_arg = self.get_query_argument('b', default=None)
        query_args = self.get_query_arguments('b')
        print(query_arg)
        print(query_args)

class HomeHandler(RequestHandler):
    
    def get(self, param1, param2):
        self.write('hello')
        
    def post(self, param1, param2):
        self.write(param1 + param2)

class PostHandler(RequestHandler):
    def get(self):
        pass
    def post(self, *arg, **kwargs):
        print(10)
        files = self.request.files
        file = files.get('avatar', '')[0]
        print(20)
        print(file.filename)
        upload_path = 'C:/Users/wangz/Desktop/xxx.png'
        print(upload_path)
        with open(upload_path, 'wb') as e:
            e.write(file.body)
        self.write("successful")
        self.write("successful")
        for f in file.body:
            print(f)
        
app = Application([
    (r'/(.+)/([a-z]+)', IndexHandler),
    (r'/index', IndexHandler),
    (r'/(?P<param1>.+)/(?P<param2>\d+)', HomeHandler),
    (r'/post', PostHandler),
])

# define('port', default=8888, help='set server port', type=int)
server = HTTPServer(app)
parse_config_file('config.py')
server.listen(options.port)
IOLoop.instance().start()
















