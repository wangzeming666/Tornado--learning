# TornadoLearn.py

# 同步函数示例
from tornado.httpclient import HTTPClient 

def synchronous_fetch(url):
	http_client = HTTPClient()
	response = http_client.fetch(url)
	return response.body


# 异步函数示例
from tornado.httpclient import AsyncHTTPClient

def asynchronous_fetch(url, callback):
	http_client = AsyncHTTPClient()
	def handle_response(response):
		callback(response.body)
	http_client.fetch(url, callback=handle_response)


# 使用Future代替回调
from tornado.concurrent import Future 

def async_fetch_future(url):
	http_client = AsyncHTTPClient()
	my_future = Future()
	fetch_future = http_client.fetch(url)
	fetch_future.add_done_callback(
		lambda f: my_future.set_result(f.result()))
	return my_future


# 协程示例
from tornado import gen
@gen.coroutine
def fetch_coroutine(url):
	http_client = AsyncHTTPClient()
	response = yield http_client.fetch(url)
	# 在Python3.3之前的版本中，从生成器函数返回一个只是不允许的
	# 必须用raise gen.return(response.body)来代替
	# coroutines  英[kəraʊ'ti:nz]


# Python 3.5引入了 async 和 await 关键字，所以
# 在tornado中可使用async和await关键字来代替yield，
# 使用了这些关键字的函数通常被叫做native coroutines 原生协程
# 简单的通过使用async def foo()来代替@gen.coroutine装饰器
# async和await在可用时会运行的更快
# 
# await	英[əˈweɪt]    async	英[ə'zɪŋk]

# 示例
async def fetch_coroutine(url):
	http_client = AsyncHTTPClient()
	response = await http_client.fetch(url)
	return response.body


# await 关键字并不像yield更加通用
# 例如在一个基于yield的协程中你可以生成一个列表的Furures，
# 但是在原生的(native)协程中你必须给列表报装tornado.gen.multi
# 你也可以使用tornado.gen.convert_yielded将使用yield的任何东西转换成用await的形式


# 原生协程不依赖于某种特定的框架（例如，tornado.gen.coroutine 或 asyncio.coroutine 装饰器）
# 不是所有的协程都和其他程序兼容
# 有一个协程运行器在第一个协程被调用时进行选择，然后被所有直接调用await的协程库共享.
# （There is a coroutine runner which is selected by the first coroutine to be called, 
# and then shared by all coroutines which are called directly with await.)
# Tornado协程运行器设计时就设定为多用途而且可以接受任何框架的awaitable对象
# 而其它协程运行器可能会有更多的限制（例如asyncio协程运行器不能接受其他框架的协程）
# 由于这个原因，推荐使用Tornado的协程运行器来兼容任何框架的协程
# 有一个在Tornado协程运行器中调用一个已经用了asyncio协程运行器的协程的适配器，
# tornado.platform.asyncio.to_asyncio_future



# 一个含有yield的函数是一个生成器。所有生成器都是异步的，调用它时将会返回一个对象而不是将函数运行完成。
# @gen.coroutine装饰器通过 yield 表达式和生成器进行通信，并随着协程的调用，返回一个Future.
# (The @gen.coroutine decorator communicates with the generator via the yield expressions, 
# and with the coroutine’s caller by returning a Future.)
# 下面是一个协程装饰器内部循环的简单版本

# Simplified inner loop of tornado.gen.Runner
def run(self):
	# send(x) makes the current yield return x.
	# It returns when the next yield is reached.
	future = self.gen.send(self.next)
	def callback(f):
		self.next = f.result()
		self.run()
	future.add_done_callback(callback)


# 装饰器从生成器接受一个Future对象，等待（非阻塞的）Future完成，然后解开Future，将结果像yield表达式的结果一样返回给生成器.
# 大多数异步代码不直接接触到Future类.除非异步函数立即通过Future返回给yield表达式.


# 协程通常不会抛出异常，任何异常将会被Future捕获，直到它被生成(untile it is yielded).
# 这意味着正确的调用协程非常重要，否则容易忽略很多错误.



# 如何调用一个协程
@gen.coroutine
def divide(x, y):
	return x / y

def bad_call():
	# This should raise a ZeroDivisionError, but it won't beacuse the coroutine is called incorrectly.
	divide(1, 0)

# 几乎在所有情况下，任何调用协程的函数本身必须是一个协程，而且使用yield关键字调用.
# 当你打算覆盖父类中的方法时，请查阅文档来判断协程是否被支持（文档中应该写到该方法是一个协程或返回Future之类）



# 有时你不想等待一个协程的返回值。Tornado推荐使用 IOLoop.spawn_callback, 他确保IOLoop负责调用，如果它失败了，
# IOLoop会在日志中记录一个跟踪栈.

# The IOLoop will catch the exception and print a stack trace in the logs. Note this that doesn't look like a normal
# call, since we pass the function object to be called by the IOLoop.
IOLoop.current().spawn_callback(divide, 1, 0)

# 最后，在程序的最顶级，如果IOLoop还没有运行，你可以启动IOLoop，使其执行你的协程，并使用IOLoop.run_sync方法停止IOLoop.
# 这通常用来启动面向批处理程序的主函数(main function).
# run_sync() doesn't take arguments, so we must wrap the call in a lambda.
IOLoop.current().run_sync(lambda: divide(1, 0))



# 协程模式
# 结合 callbacks
# 为了使用callbacks代替Future与异步代码交互, 将调用包装在Task中，
# 这将为你添加回调参数，并返回一个可以 yield 的 Future.
# （To interact with asynchronous code that uses callbacks instead of Future, wrap the call in a Task. 
# This will add the callback argument for you and return a Future which you can yield:）
@gen.coroutine
def call_task():
	# Note that there are no parens on some_function.
	# This will be translated by Task into some_function(other_args, callback=callback)
	yield gen.Task(some_function, other_args)


# 调用阻塞函数
# 从一个协程调用阻塞函数最简单的方法是使用 ThreadPoolExecutor, 返回与协程兼容的 Futures： 
thread_pool = ThreadPoolExecutor(4)

@gen.coroutine
def call_blocking():
	yield thread_pool.submit(blocking_func, args)


# 并行
# 协程装饰器能识别 Futures 的列表和字典中的值， 并等待所有的 Futures 并行
@gen.coroutine
def parallel_fetch(url1, url2):
	resp1, resp2 = yield [http_client.fetch(url1),
						  http_client.fetch(url2)]

@gen.coroutine
def parallel_fetch_many(urls):
	responses = yield [http_client.fetch(url) for url in urls]
	# responses is a list of HTTPResponses in the same ordler

@gen.coroutine
def parallel_fetch_dict(urls):
	responses = yield {url: http_client.fetch(url) for url in in urls}
	# responses is a dict {url: HTTPResponse}


# 交错模式：数据交错存取技术(也叫交叉存取技术)
# 有时存储一个 Future 比立刻迭代它更有用，这样你可以在等待完成前做其他的运算
@gen.coroutine
def get(self):
	fetch_future = self.fetch_next_chunk()
	# chunk 数据块
	while True:
		chunk = yield fetch_future
		if chunk is None : break
		self.write(chunk)
		fetch_future = self.fetch_next_chunk()
		yield self.flush()

# 此模式通常和 @gen.coroutine 一同使用. 如果 fetch_next_chunk() 使用 async def, 那它必须被 fetch_next_chunk() 调用，
# 用以开始后台处理（后台处理是一般处于次优先地位的处理）


# 循环
# 自从Python中没有任何一种循环器中可以使用 yield 以后，loop 协程和捕捉 yield 的结果就变得棘手
# 取而代之的是，你需要将对结果的访问从循环环境中分离出来，
# 这里有一个 Motor 的例子
import motor 
db = motor.MotorClient().test

@gen.coroutinedef 
def loop_example(collection):
	cursor = db.collection.find()
	while (yield cursor.fetch_next):
		doc = cursor.next_object()


# 后台运行
# PeriodicCallback 不常与协程一同使用. 取而代之的是，一个协程可以包含一个 while true： 
# 循环并使用 tornado.gen.sleep:
@gen.coroutine
def minute_loop():
	while True:
		yield do_something()
		yield gen.sleep(60)

# Coroutine that loop forever are generally started with spawn_callback().
IOLoop.current().spawn_callback(minute_loop)


# complicated  英[ˈkɒmplɪkeɪtɪd]  adj.	结构复杂的; 混乱的，麻烦的;
# desirable	英[dɪˈzaɪərəbl]  adj.	可取的; 令人满意的; 值得拥有的; 性感的;
# previous	英[ˈpri:viəs]  adj.	以前的; 先前的; 过早的; （时间上） 稍前的;
# 有时一个更复杂的循环可能会更令人满意. 例如，之前的循环每 60+N 秒运行一次，N 是运行 do_something() 的时间.
# 要想精确地每 60 秒运行一次，使用之前提到的交叉模式：
@gen.coroutine
def minute_loop2():
	while True:
		nxt = gen.sleep(60)     # start the clock.
		yield do_something		# Run while the clock is ticking.
		yield nxt 				# Wait for the timer to run out.




# Queue——并发网络爬虫
# Tornado的 Tornado.queues 模块对与协程实现了异步的生产者/消费者模型，实现了类似于Python标准库中线程中的queue模块.

# 一个yield Queue.get 的协程会暂停，直到队列中有队列中有值时运行.
# 如果队列被设置了最大值，一个yield 的协程会暂停，直到有空间存放新的迭代值.

# Queue 从零开始维护了一系列未完成的任务. put 增加计数， task_done 减少它.

# 在这个网络爬虫的示例中，队列开始只包含 base_url. 当一个 worker 匹配到一个页面，它会将连接解析并放进一个新的队列中，
# 然后调用 task_done 减少一次计数. 最终一个 worker 匹配的一个页面里的URL都是之前匹配过的，而且没有工作留在队列中.
# worker 调用 task_down 将计数减至0. 主协程等待 join 取消暂停并完成.
#!/usr/bin/env python

import time
from datetime import timedelta

try:
	from HTMLParser import HTMLParser
	from urlparse import urlJoin, urldefrag
except ImportError:
	from html.parser import HTMLParser
	from urllib.parse import urljoin, urldefrag

from tornado improt httpclient, gen, ioloop, queues

base_url = 'http://www.tornadoweb.org/en/stable/'
concurrency = 10

@gen.coroutine
def get_links_from_url(url):
	"""Download the page at 'url' and parse it for links.

	Returned links have had fragment after '#' removed, and have been made absolute so,
	e.g. the URL 'gen.html#gen.coroutine' becomes 'http://www.tornadoweb.org/en/stable/gen.html'
	"""
	try:
		response = yield httpclient.AsyncHTTPClient.fetch(url)
		print('fetched %s' % url)

		html = response.body if isinstance(response.body, str) \
		else response.body.decode()
		urls = [urljoin(url, remove_fragment(new_url)) for new_url in getlinks(html)]
		# urllib.parse.urljoin(base, url, allow_fragments=True) # Python 标准库
		# Construct a full (“absolute”) URL by combining a “base URL” (base) with another URL (url). 
	except Exception as e:
		print('Exception: %s %s' % (e, url))
		raise gen.Return([])
		# (我猜这里raise是因为协程会捕捉异常，除非协程被yield，否则异常无法抛出)

	raise gen.Return(urls)


def remove_fragment(url):
	pure_url, frag = urldefrag(url)
	# urllib.parse.urldefrag(url) # Python 标准库
	# If url contains a fragment identifier, return a modified version of url with no fragment identifier, 
	# and the fragment identifier as a separate string.
	return pure_url


def get_links(html):
	class URLSeeker(HTMLParser):
		def __init__(self):
			HTMLParser.__init__(self)
			self.urls = []

		def handler_starttag(self, tag, attrs):
			# dict.get(key, default=None) # Python 列表方法
			# 如果列表中存在key的值，返回值，不存在则返回default默认值
			href = dict(attrs).get('href')
			if href and tag == 'a':
				self.urls.append(href)

	url_seeker = URLSeeker()
	# HTMLParser.feed(data) # Python 标准库
	# Feed some text to the parser.
	url_seeker.feed(html)


@gen.coroutine
def main()
	q = queues.Queue()
	# time.time() 返回自纪元以来的秒数时间
	start = time.time()
	fetching, fetched = set(), set()

	@gen.coroutine
	def fetch_url():
		current_url = yield q.get()
		try:
			if current_url in fetching:
				return

			print('fetching %' % current_url)
			fetching.add(current_url)
			urls = yield get_links_from_url(current_url)
			fetched.add(current_url)

			for new_url in urls:
				# beneath	英[bɪˈni:θ]  prep.	在…的下方; （表示等级） 低于;
				# (表示状态） 在…掩饰之下; （表示环境） 在…影响之下;  adv.	在下面; 在底下;
				# Only follow links beneath the base URL
				# str.startswith(str, beg=0,end=len(string));
				# Python startswith() 方法用于检查字符串是否是以指定子字符串开头，
				# 如果是则返回 True，否则返回 False。如果参数 beg 和 end 指定值，则在指定范围内检查.
				if new_url.startswith(base_url):
					yield q.put(new_url)

		finally:
			q.task_done()

	@gen.coroutine
	def worker():
		while True:
			yield fetch_url()

	q.put(base_url)

	# Start workers, then wait for the work queue to be empty.
	for _ in range(concurrency):
		worker()
	# 超時終止
	yield q.join(timeout=timedelta(seconds=300))
	assert fetching == fetched
	print('Done in %d seconds, fetched %s URLs.' %(time.time() - start, len(fetched)))


if __name__ == '__main__':
	# logging: 该模块定义了为应用程序和库实现灵活的事件日志记录系统的函数和类
	# logging.basicConfig(): 通过创建默认值并将其添加到根记录器中来记录日志系统的基本配置
	import logging
	logging.basicConfig()
	io_loop = ioloop.IOLoop.current()
	io_loop.run_sync(main)





# Tornado 应用程序结构
# Tornado web 应用程序通常包含一个或多个RequestHandler子类，一个Application对象来为每个控制器路由到达的请求，
# 和一个main()方法来启动服务器
# 一个小型示例
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello, world!")

	def make_app():
		return tornado.web.Aoolication([
			(r"/", Mainhandler),
			])

if __name__ == '__main__':
	app = make_app()
	appp.listen(8888)
	tornado.ioloop.IOLoop.current().start()


# Application对象用来负责全局的设置，包括用来转发请求到控制器的路由表.
# 路由表是一个URLSpec对象(或元组)的列表，每一个表至少包含一个正则表达式和一个handler类
# 按照顺序，第一个匹配规则被使用. 如果正则表达式包含捕获组，则这些组作为路径参数传给handler的HTTP方法     
# 如果一个字典作为第三个参数传给URLSpec，它提供初始化参数，被传递到RequestHandler.initialize.
# 最终，URLSpec 可能会有一个名字，允许与 RequestHandler.reverse_url 一同使用.
# 例如，在这个片段中跟URL / 被匹配到Main Handler，而表单的URL /story/ 跟着一个数字，可以被匹配到StoryHandler
# 这个数字作为字符串传递给StoryHandler.get.
class MainHandler(RequestHandler):
	def get(self):
		self.write('<a href="%s">link to story 1</a>' % self.reverse_url("story", "1"))

class StoryHandler(RequestHandler):
	def initialize(self, db):
		self.db = db

	def get(self, story_id):
		self.write("this is story %s" % sotry_id)

app = Application([
	url(r'/', MainHandler),
	url(r'/story/([0-9]+)', StoryHandler, dict(db=db), name='story')
	])

# 这个Application构造器接受许多关键字参数，可以被用来定制适用的行为和开启特定功能. 可以官网查看Application.settings完整列表.



# RequestHandler子类
# 几乎所有的Tornado web application 都在RequestHandler子类中被完成. 
# 对于一个handler子类来说主要的入口点是一个以处理HTTP方法名命名的方法：如get(), post()
# 每个handler 可能定义一个或多个方法去处理不同的HTTP功能. 如上所述，这些方法将被匹配到路由规则匹配的捕获组，作为参数调用.
# 在一个handler内，调用如RequestHandler.render 或 RequestHandler.write 来创建一个response(n.响应，回答).
# render()以提供的参数名字加载一个Template(模板)并renders(递交)它.
# write()被用在没有template基本模板的时候，它可以接受字符串、字节码和多个字典(字典将被转换为JSON格式).

# 许多RequestHandler中的方法都被设计为可以在子类中被覆盖，在整个应用程序中使用.
# 为具体的handler需求定义一个BaseHandler类覆写如write_error 和 get_current_user 
# 以及子类化有自己的BaseHandler代替RequestHandler 是一件很平常的事.



# 处理输入请求
# 请求handler可以从 self.request 获取当前请求的对象. 查看HTTPServerRequest类定义来获取完成属性列表.

# HTML表单形式的数据由 get_query_argument 和 get_body_argument 实现格式转换.
class MyFormHandler(tornado.web.RequestHandler):
	def get(self):
		self.write('<html><body><form action="/myform" method="POST">'
				   '<input type="text" name="message">'
				   '<input type="submit" value="value="Submit">'
				   '</form></body></html')
	
	def post(self):
		self.set_header("Content-Type", "text/plain")
		self.write("You wrote" + self.get_body_argument("message"))

# HTML表单编码模糊单值参数和单值列表，RequestHandler有明确的方法允许application声明想要的是不是一个列表.
# 对于列表，使用 get_query_argument 和 get_body_arguments 代替他们的单数用法.

# 通过表单上传文件可在self.request.files中获得，它映射名字(HTML中<inpu type='file'>的名字)到文件列表.
# 每个文件都是表单的字典 {'filename':..., 'content_type':..., 'body':...}
# files对象只会在文件对象以表单wrapper(就是一个multipart/form-data Content-Type)上传时出现.
# 如果这种形式没有被使用，原始上传数据是在self.request.body中获取.
# 随着默认上传文件充满了缓存记忆区，如果你需要更充裕地处理过大的文件保存在记忆区，查看stream_request_body类装饰器.

# file_reciever.py展示了这两种接受上传文件的方法，文件如下
#!/usr/bin/env python

"""Usage: python file_receiver.py
Demonstrates a server that receives a multipart-form-encoded set of files in an
HTTP POST, or streams in the raw data of a single file in an HTTP PUT.
See file_uploader.py in this directory for code that uploads files in this format.
"""

import logging

try:
    from urllib.parse import unquote
except ImportError:
    # Python 2.
    from urllib import unquote

import tornado.ioloop
import tornado.web
from tornado import options


class POSTHandler(tornado.web.RequestHandler):
    def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logging.info('POST "%s" "%s" %d bytes',
                             filename, content_type, len(body))

        self.write('OK')


@tornado.web.stream_request_body
class PUTHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.bytes_read = 0

    def data_received(self, chunk):
        self.bytes_read += len(chunk)

    def put(self, filename):
        filename = unquote(filename)
        mtype = self.request.headers.get('Content-Type')
        logging.info('PUT "%s" "%s" %d bytes', filename, mtype, self.bytes_read)
        self.write('OK')


def make_app():
    return tornado.web.Application([
        (r"/post", POSTHandler),
        (r"/(.*)", PUTHandler),
    ])


if __name__ == "__main__":
    # Tornado configures logging.
    options.parse_command_line()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

# 由于HTML的编码十分怪异(例如单数与复数参数的含糊不清). Tornado不会去试图统一输入类型的参数.
# 特别是不会解析JSON请求体. 应用程序想要使用JSON代替表单编码可能要覆写 prepare 来解析它们的请求.
def prepare(self):
	if self.request.headers['Content-Type'].startswith('application/json'):
		self.json_args = json.loads(self.request.body)
	else:
		self.json_args = None



# 覆写RequestiHandler方法
# 除了 get()/post()等，在RequestHandler中的全部方法都被定义为能在必要时被子类覆写.
# 在每个请求中，按下面的调用顺序
# 1.一个新的RequestHandler对象被创建在每一次请求中
# 2.initialize()和Application配置的初始化参数一同被调用. initialize应通常只保存传递给成员变量的参数。
#   它可能不创建任何输出或调用任何方法，像send_error一样.
# 3.prepare()被调用. 这是一个在基础类中最有用的，被所有你得handler子类分享.
#   无论哪个HTTP方法被调用，prepare都被调用. prepare可能创建输出.如果prepare调用finish(或redirect等)，处理在这停止.
# 4.一个HTTP方法被调用: get(), post(), put()等. 如果URL正则表达式包含捕获组，它们作为参数传递给这个方法.
# 5.当请求完成，on_finish()被调用. 在同步处理中在get()等之后里立即返回，在异步处理中这一步会在调用finish()之后执行。

# 所有像这样可以被覆盖的方法都记录在 RequestHandler 的文档中. 一些最常用的覆写方法包括：
# write_error - 输出用于错误页面的HTML.
# on_connection_close - 当客户端断开时被调用，应用程序可以选择检测此情况并中止进一步处理. 
# 注意这里不保证一个关闭的链接能被立刻检测到.
# get_current_user - 用户认证. 查看User authentication文档获取更多信息.
# get_user_locate - 返回Locate对象提供当前用户使用.
# set_default_handers - 可以被用来在响应上附加标头(例如一个自定义Server头).



# 错误处理
# 如果一个handler抛出了一个异常，Tornado将调用RequestHandler.write_erroe 生成一个错误页面；
# tornado.web.HTTPError能被用来生成特定的状态码，其它异常抛出抛出返回一个500状态.

# 默认错误页面包括一个调试模式的堆栈跟踪，和一个只有一行的错误描述(例如，500:Internal Server Error).
# 通过覆写RequestHandler.write_error来创建一个自定义错误页面(可能在一个基类中被所有handlers共享).
# 此方法通常可以通过write和render方法创建输出. 如果错误由异常引起，一个exc_info组将被作为关键字参数(注意，这个异常
# 不能确保一定是当前在sys.exc_info中的错误, 所以write_error必须使用例如traceback.format_exception代替traceback.format_exc).

# 也可以以一般的处理方法生成一个错误页面代替通过set_tatus调用write_error，写一个响应并返回. 
# 在不方便简单返回的情况下，特殊的异常tornado.web.Finish可能被抛出来结束处理而不调用write_error.

# 对于错误404，使用default_handler_class Application setting. 这个处理应该覆写prepare来代替更复杂的方法比如get()，
# 以便它可以和任何HTTP方法一共工作. 它应创建它的错误页面来描述：通过抛出一个HTTPError(404)并覆写write_error, 
# 或调用self.set_status(404)并在prepare()中创建立即响应.



# 重定向
# 在Tornado中有两种主要的方法可以重定向响应：RequestHandler.redirect 和 RedirectHandler. 

# 你可以在RequestHandler方法里面使用self.redirect()来重定向其它使用者.
# 也有一个选项参数permanent可以使用，用来标明重定向被认为是永久的.
# permanent默认值为False，生成一个302Found HTTP相应代码并适用于在POST响应成功后重定向users(不知道改翻译成用户还是使用者).
# 如果permanent值为True，301 Moved Permanently HTTP 响应码被使用，这对例如重定向到 a page in an SEO-friendly manner.
# (怎么也翻译不过来上一句，术语查不到).

# RedirectHandler 让你直接在你的Application路由表里配置重定向. 例如，配置一个单独的静态重定向.
app = tornado.web.Application([
	url(r'/app', tornado.web.RequestHandler, dict(url='http://itunes.apple.com/my-app-id')),
	])

# RedirectHandler 也支持正则表达式替换. 下面的规则重定向所有以/pictures/开头的响应，以/photos/前缀代替.
app = tornado.web.Application([
	url(r'/photos/(.*)', MyPhotoHandler),
	url(r'/hictures/(.*)', tornado.web.RedirectHandler, dict(url=r'/photos/{0}')),
	])

# 不同于RequestHandler.redirect，RedirectHandler使用默认值来永久重定向. 这是因为路由表在执行过程中不会改变，并被假定是永久的，
# 当重定向发现可能的其它程序逻辑时可能会发生改变. 用RedirectHandler发送一个临时的重定向，添加permanent=False到RedirectHandler的
# 初始化参数中.




# 异步处理
# Tornado处理是默认同步的：当get()/post()方法返回，请求被视为完成并且响应被发送. 当一个处理(handler)正在执行时，
# 其它所有的请求被阻塞, 任何长时间运行的处理都应该被异步，这样程序可以在不阻塞的情况下调用它的慢速运算.
# 这个议题的更多细节被包括在Asynchronous and non-Blocking I/O; 这部分关于异步的技术细节在RequestHandler子类中.

# 最简单的创建一个处理异步的方法是使用coroutine装饰器. 这允许你以yield关键字进行非阻塞I/O，直到coroutine返回前，响应不会被发送.
# 查看 Coroutines 可以获取更多细节.

# 在某些情况中，协程可能没有基于回调的风格更方便，在这种情况下tornado.web.asynchronous装饰器能被用来代替((may be) coroutine). 
# 当这个装饰器被使用，响应不会自动送出；相反的是请求会被保持开放直到一些回调函数调用RequestHandler.finish. 
# 这需要应用程序确保这个方法被调用，否则用户的浏览器会被简单挂起. 

# 这是一个使用Tornado内建的AsyncHTTPClien调用FriendDeed API 的例子：
class MainHandler(tornado.web.RequestHandler):
	@tornado.web.AsyncHTTPClient()
	def get(self):
		http = tornado.httpclient.AsyncHTTPClient()
		http.fetch('http://friendfeed-api.com/v2/feed/bret', callback=self.on_response)

	def on_response(self.response):
		if response.error: raise tornado.web.HTTPError(500)
		json = tornado.escape.json_decode(response.body)
		self.write('Fetched' + str(len(json['entries'])) + 'entries' 'from the FriendFeed API')   # 文档这么写的，空格
		self.finish()

# 当get()返回，请求还没有完成. 当HTTP客户端最后一步调用on_response()，请求仍然开放，调用self.finish()响应最终发出.
# 作为比较，这是使用协程的相同例子:
class MainHandler(tornado.web.RequestHandler):
	@tornado.gen.coroutine
	def get(self):
		http = tornado.httpclient.AsyncHTTPClient()
		response = yield http.fetch('http://friendfeed-api.com/v2/feed/bret')
		json = tornado.escape.json_decode(response.body)
		self.write('Fetched' + str(len(json['entries'])) + 'entries' 'from the FriendFeed API')、

# 获取更多异步示例建议，请查看chat example application，它使用长轮询实现一个AJAX聊天室. 
# 长轮询使用者可能想要覆写on_connection_close()来在客户端关闭后清除链接(但请查看该方法的文档获取警告信息).




# 模板和用户界面
# Tornado包含一个简单、高速，并且灵活的模板语言. 本节描述了语言以及国际化等相关问题.

# Tornado 可以与其他Python模板语言一同使用，尽管没有将这些系统整合到RequestHandler.render中. 
# 非常简单的通过RequestHandler.write将模板递交给一个字符串即可.

# 配置模板
# 通过默认值，Tornado在与.py文件相同的目录中查找所关联的模板文件. 
# 使用template_path Application setting，来放入你的不同目录下的模板文件(或覆写RequestHandler.get_template_path
# 如果你的不同handlers有不同的模板路径).

# 从非文件系统位置加载模板，应子类化tornado.template.BaseLoader并传递一个实例作为 template_loader应用设置.

# 默认情况下编译的模板会被缓存；关闭缓存和重加载模板来改变底层文件总是可见，使用应用设置compiled_template_cache=False
# 或debug=Ture.

# 模板缩进

# 一个Tornado模板只是HTML(或任何其他的文本基础格式)与嵌入在标签中的控制组和表达式.
<html>
	<head>
		<title>{{ title }}</title>
	</head>
	<body>
		<ul>
		{% for item in items %}
			<li>{{ escape(item) }}</li>
		{% end %}
		</ul>
	</body>
<html>

# 如果你保存这个模板为template.html并与Python文件放入相同的目录中，你可以像这样递交模板：
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		items = ['Item 1', 'Item 2', 'Item 3']
		self.render('template. html', title='My title', items=items)

# Tornado模板支持控制声明和表达式. 控制声明被 '{%' 和 '%}' 包围，例如{% if len(items) > 2 %}.
# 表达式被{{ }}包围，例如，{{ items[0] }}

# 控制语句多多少少映射了Python语句. 我们支持if，for，while 和 try，所有这些都以{% end %}结束. 
# 我们也支持模板继承使用entends和block语句，它们的细节在tornado.template中被详细描述.

# 表达式可以是任何Python表达式，包括函数调用. 模块代码被执行在一个包含下列对象和函数的命名空间
# (注意此表适用于使用requesthandler.render和render_string渲染模板. 如果你在RequestHandler外直接使用tornado.template,
# 这里的许多条目是不存在的). 

	# escape: 				别名 tornado.escape.xhtml_escape
	# xhtml_escape: 		别名 tornado.escape.xhtml_esvape
	# url_escape: 			别名 tornado.escape.url_escape
	# json_encode: 			别名 tornado.escape.json_encode
	# squeeze： 				别名 tornado.escape.squeeze
	# linkify: 				别名 tornado.escape.linkify
	# datetime: 			Python datetime 模块
	# handler: 				当前RequestHandler对象
	# request: 				别名 handler.request
	# current_user  		别名 handler.current_user
	# local					别名 handler.locale
	# _ 					别名 handler.locale.translate
	# static_url 			别名 handler.static_url
	# xsrf_form_html		别名 handler.xsrf_form_html
	# reverse_url			别名 Application.reverse_url
	# 所有条目来自ui_methods 和 ui_modules Application设置
	# 任何关键字参数传给render或render_string

# 当你正在创建一个真实的应用时，你会想去使用所有的Tornado模板特性，尤其是模板继承.
# 在tornado.template部分阅读所有相关特性(一些特性，包括UIMoudles被实现在tornado.web模块).

# 在引擎下，Tornado模块立即被翻译给Python. 在你模板中包含的表达式被逐字复制入一个Python函数代表你的模板. 
# 我们不会试图阻止模板语言中的任何事，我们显示的创建它以提供其它更严格的模板系统所避免的灵活性.
# 因此，如果在模板表达式中写入随机内容，则在执行模板时将获得随机的Python错误.

# 所有模板输出默认使用tornado.escape.xhtml_eacape方法被捕获. 此行为可以被改变，通过在全局内传递autoescapt=None给Application 或
# tornado.template.Loader构造器，对一个模板文件使用
# {% autoescape None %}指明，或是使用一个单独的表达式{% raw ...%} 替换 {% .. %}.
# 此外，在这些设置的每一处可以使用可替代的转义函数名来代替None.(翻译的应该没错，不明白什么意思)

# 注意Tornado的自动转义在回避 XSS跨站攻击脚本时是非常有用的, 它不足以用于所有情况. 
# 表达式出现在某些位置如Javascript或CSS中，可能需要附加转义. 此外也要注意必须在HTML的属性内容中不可信的内容处一直使用双引号和 
# xhtml_escape, 或是使用一个单独的转义函数来代替这些方法. 可查看示例 http://wonko.com/post/html-escaping.


# 国际化
# 当前用户的locale(区域位置)(登陆与否)总是可获得的，在请求handler中是 self.locale，在模板中为 locale. 
# locale的名字(例如en_US)可从 locale.name 获得，使用Local.translate方法能翻译字符串.
# 模板也有名为 _() 的全局函数来翻译字符串. 翻译函数有两种形式：
_("Translate this string")

# 这种方法基于当前区域立即翻译字符串，而
_("A person liked this", "%(num)d people liked this", len(people)) % {"num": len(people)}

# 这种翻译方法能翻译一个或多个字符串，基于第三参数变量的值. 在上面的例子中，如果len(people)为 1，第一个字符串的翻译会被返回. 
# 否则第二个字符的字符串会被翻译并返回. 

# 最常见的翻译模式是对变量使用 Python命名占位符(例如上面的%(num)d)，这是由于占位符可以在翻译的时移动.
# 这是个合适的国际化模板.
<html>
	<head>
		<title>FriendFeed - {{ _("Sign in") }}</title>
	</head>
	<body>
		<form action="{{ request.path }}" method="post">
			<div>{{ _("Username") }} <input type="text" name="username"/></div>
			<div>{{ _("Password") }} <input type="password" name="pass"/></div>
			<div><input type="submit" value="{{ _("sign in") }}"/></div>
			{% module xsrf_form_html() %}
		</form>
	</body>
</html>

# 默认使用从用户浏览器发送的 Accept-Language 头检测用户的区域. 如果找不到一个合适的Accept-Language值则选择en_US.
# 如果你让用户的设置作为他们区域的优先选择，你可以通过覆写 RequestHandler.get_user_locale 以覆盖默认区域选项.
class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		user_id = self.get_secure_cookie('user')
		if not user_id: return None
		return self.backend.get_user_by_id(user_id)

	def get_user_locale(self):
		if 'locale' not in self.current_user.prefs:
			# Use the Accept-Language header
			return None
		return self.current_user.prefs['locale']

# 如果 get_user_locale 返回None，我们转而依靠Accept-Language来实现.

# tornado.locale 模块支持两种形式加载翻译： .mo 形式使用 gettext 和与之相关的工具，另一个是简单的 .csv 形式.
# 一个application通常在启动时调用 tornado.loacle.load_translations 或 tornado.locale.load_gettext_translations二者中的一个,
# 查看这些方法得到所支持格式的更多细节.

# 你可以在你的application中使用 tornado.locale.get_supported_locales() 得到支持的区域列表. 
# 用户的区域被选择为匹配到的与所支持的区域的最接近的. 例如，如果用户的区域是 es_GT，并支持 es 区域，self.locale 的请求就会是 es.
# 如果匹配没被找到，则使用 en_US.


# UI 模块
# Tornado 支持 UI模块，这使在你的应用中支持标准、可重用的UI工具变得容易. 
# UI模块像是提交你的页面组件的特殊函数调用，他们能将自身的 CSS 和 JS代码一同打包. 

# 例如，如果你正在实现一个博客，而且你想你的博客条目出现在你的博客主页和每个博客条目页，你可以写一个条目模块来在每一个页面提交.
# 首先，为你的 UI模块创建一个 Python模块，例如:
# uimodules.py
class Entry(tornado.web.UIModules):
	def render(self, entry, show_comments=False):
		return self.render_string('module-entry.html', entry=entry, show_comments=show_comments)

# 告诉 Tornado 去使用 uimodules.py, 使用 ui_modules 在你的application中设置.
from .import uimodules

class HomeHandler(tornado.web.RequestHandler):
	def get(self):
		entries =self.db.query("SELECT * FROM entries ORDER BY date DESC")
		self.render("home.html", entries=entries)

class EntryHandler(tornado.web.RequestHandler):
	def get(self, entry_id):
		entry = self.db.get("SELECT * FROM entries WHERE id = %s", entry_id)
		if not entry: raise tornado.web.HTTPError(404)
		self.render("entry.html", entry=entry)

settings = {
	"ui_modules": uimodules,
}
application = tornado.web.Application([
	(r'/', HomeHandler),
	(r'/entry/([0-9]+)', EntryHandler),
	], **settings)

# 在一个模板中，你可以以 {% module %} 调用一个模块. 例如，你可以从 home.html 中调用 Entry 模块：
{% for entry in entries %}
	{% module Entry(entry) %}
{% end %}

# 或是从entry.html中调用：
{% module Entry(entry, show_comments=True) %}

# 模块可以通过覆写 embedded_css, embeded_javascript, javascript_files或 css_files方法 来定制 CSS 和 JS函数：
class Entry(tornado.web.UIModules):
	def embedded_css(self):
		return '.entry { margin-bottom: 1em; }'

	def render(self, entry, show_comments=False):
		return self.render_string('module-entry.html', show_comments=show_comments)

# 在一个页面上无论一个模块被使用多少次，CSS 和 JS 模块只被 include(插入??) 一次. CSS 总是在页面的 <head> 部分被 include，
# JS总是在页面底部的 </body>标签前被include.

# 当不需要附加的 Python代码时，一个模板文件本身可以被用作一个模块. 例如，前面的例子可以被改写为在module-entry.html中放入下面代码：
{{ set_resources(embedded_css=".entry { margin-bottom: 1em; }") }}
' <!-- more template... --> # 此行为html注释'

# 这个修改过的模板模块将被调用
{% module Template("module-entry.html", show_comments=True) %}

# set_resources 函数仅在模板通过 {% module Template(...) %} 调用时才可获得. 不同于 {% include ... %}指令，
# 模板模块有一个来自它们的包含模板的特有命名空间，----它们仅仅能看到局部模板命名空间和它们自己的参数.




# 安全认证
# cookie 和 secure cookie

# 你可以使用 set_cookie 方法在用户的浏览器设置 cookies：
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		if not self.get_cookie('mycookie'):
			self.set_cookie('mycookie', 'myvalue')
			self.write('Your cookie was not set yet!')
		else:
			self.write('Your cookie was set!')

# Cookies 是非常不安全的，可以被客户端随意修改. 如果你需要设置 cookie，例如确定当前登陆用户，你需要签署你的cookies 以避免被伪造.
# Tornado 支持以 set_secure_cookie 和 get_secure_cookie 方法签名cookie. 使用这些方法，你需要在你创建你的应用时指定一个
# 名为 cookie_secret的密钥. 你可以在application 中设置关键字参数来到你的应用：
application = tornado.web.Application([
	(r'/', MainHandler),
	], cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE___") 

# 对cookie签名包括添加cookie的编码值、时间戳和一个哈希信息验证码(HMAC)签名. 如果cookie过期或是签名不匹配，get_secure_cookie 
# 会返回 None，就像cookie 没有被设置时一样. 上面例子的安全版本：
class MainHandler(tornado.web.RequestHandler):
	def get(self):
		if not self.get_secure_cookie('mycookie'):
			self.set_secure_cookie('mycookie', 'myvalue')
			self.write("Your cookie was not set yet!")
		else:
			self.write("Your cookie was set!")

# Tornado 的安全签名确保完整却不保密. 就是说，cookie不能被修改，但是它的内容可以被用户识别. cookie_secret 是一个对称密钥，
# 必须被保密. 任何得到钥匙的人都可以创作他们自己签字的cookie. 

# 默认情况下，Tornado