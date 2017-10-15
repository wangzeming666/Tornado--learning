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
# 为与异步代码交互而使用callbacks代替Future, 将调用包装在Task中.
# 这将为你添加回调参数，并返回一个可以 yield 的 Future.
# （To interact with asynchronous code that uses callbacks instead of Future, wrap the call in a Task. 
# This will add the callback argument for you and return a Future which you can yield:）
@gen.coroutine
def call_task():
	# Note that there are no parens on some_function.
	# This will be translated by Task into some_function(other_args, callback=callback)
	yield gen.Task(some_function, other_args)



