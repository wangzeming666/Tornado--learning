# Tornado._concurrent_Learn.py
# tornado.concurrent--使用线程和futures工作
# 
# 与线程和Futures工作的实用工具
# 
# Futures 是一个并发的程序模式，引自Python3.2 concurrent.futures包.
# 这个包定义一个最兼容的Future类，被设计为在协程中使用，也有一些功能函数用以与concurrent.futures包交互.
# 
# 
# class tornado.concurrent.Future
# 
# 一个异步结果的占位符
# Future封装一个异步操作的结果. 在同步应用Futures被用来等带一个线程或进程池的结果；在Tornado它们通常被与
# IOLoop.add_future一同使用，或在 gen.coroutine中 yield.
# 
# tornado.concurrent.Future很像concurren.futures.Future，但不是线程安全(因此能更快的与单线程时间循环使用.
# 
# 此外 exception 和 set_exception，在Python 2中，方法 exc_info 和 set_exc_info被支持捕获回溯(tracebacks).
# 在Python3中，回溯被自动获取. 但Python2 futures back 信息被丢弃(Backport是将一个软件的补丁应用到比此补丁所对应的版本更老的版本的行为。)
# 这个功能在以前可以从分离出来的TracebackFuture获取，但现在被弃用.
# 
# 在4.0中：tornado.concurrent.,Future始终是一个线程不安全的Future，支持exc_info方法.
# 在此之前，它是线程安全的concurrent.futures.Future. 如果这个包无法被获得，则回落到非线程安全的方式执行.
# 
# 在4.1版本中，如果Future包含一个错误但没有被发现(调用result(), exception(), 或exc_info()来找到错误 )，
# 一个堆栈追踪会被记录，when the Future is garbage collected. 这通常表明一个错误在应用中，但在这种情况下，
# 不希望得到的结果可能必须被抑制，以保证异常被注意到：f.add_done_callback(lambda f: f.exception()).



# 消费者方法

# Future.result(timeout=None)
# 如果操作成功，返回它的结果. 如果失败，重新抛出异常.
# 这个方法携带一个timeout参数，以兼容concurrent.futures.Future，但是它在Furure完成前调用会发生错误，所以timeout从没被使用过.

# Future.exception(timeout=None)
# 如果操作抛出一个异常，返回异常对象. 其它情况返回None.
# 这个方法携带一个timeout参数以兼容concurrent.futures.Future，但是在Future完成前调用会出错，不被使用.

# Future.exc_info()
# 以与sys.exc_info相同的形式返回一个元组或什么都不返回. 
		# --------------------------------------------------------------------------------------------------
		# 取自Python标准库
		# sys.exc_info()
		# 这个函数返回一个三个值的元组，给出关于当前处理异常的信息. 返回的信息特定于当前的线程和当前的堆栈帧.
		# 如果当前的堆栈帧没有处理异常，则从调用者的堆栈帧、调用者的调用者等等获取信息，直到找到正在处理异常的堆栈帧. 
		# 这里，'处理异常'被定义为'执行一个except子句'. 对于任何堆栈帧，只有当前处理的异常的信息是可访问的.
		# 如果堆栈帧上没有正在处理的异常，则返回包含三个None值的元组. 否则，返回(type, value, traceback).
		# 他们的含义是：type获取正在处理的类型(BaseException的子类)；value获取异常实例(异常类型的实例)；
		# traceback获取一个跟踪对象(参见手册)，他将调用堆栈封装在异常最初发生的点.
		# --------------------------------------------------------------------------------------------------

# Future.add_done_callback(fn)
# 将给定的回调连接到Future.
# 在Future完成运行并获取到结果时，它将被调用并作为Future的参数.
# 在Tornado解释器中会立即使用IOLoop.add_future代替add_done_callback.

# Future.running()
# 如果当前操作正在运行，返回True.

# Future.done()
# 如果future已完成运行，返回True.

# Future.cancel()
# 如果可能，取消操作.
# Tornado Futures 不支持取消，所以这个方法总是返回False.

# Future.cancelled()
# 如果操作被取消，返回True.
# Tornado Futures 不支持取消，所以这个方法总是返回False.



# 生产者方法

# Future.set_result(result)
# 设置Future的结果.
# 在同一对象调用任何设置的方法超过一次的结果不明

# Future.set_exception(exception)
# 设置Future的异常.

# Future.set_exc_info(exc_info)
# 设置Future的异常信息.
# 在Python 2中保存(preserves)回溯(tracebacks)

# Future.concurrent.run_on_executor(*args, **kwargs)
# 装饰器在执行器上异步运行同步方法.
# 装饰方法可以被以callback关键字参数调用并返回一个future.
# IOLoop和执行器的使用取决于 io_loop和 self的 executor属性. 传递关键字参数给装饰器，以使用不同属性.
@run_on_executor(executor='_thread_pool')
def foo(self):
	pass
# 在4.2版本更改：添加关键字参数以使用可选的属性.



# tornado.concurrent.return_future(f)

# 装饰器确保一个函数返回通过回调函数返回的一个Future.

# 包装的函数应携带一个callback关键字参数并在它完成时使用一个参数调用它. 
# To signal failure(may be 信号故障)，函数只能抛出一个异常(将会被StackContext 捕获并单独传递给Future).

# 从调用者的角度来看，回调参数是可选的. 如果一个回调参数被给出，当函数以Future.result()结束,它会被作为参数调用.
# 如果函数失败，回调函数不会被运行，而一个异常会被抛出到StackContext环境中.
# 用法：
@return_future
def future_func(arg1, arg2, callback):
	# Do stuff (possibly asynchronous)
	callback(result)

@gen.engine
def caller(callback):
	yield future_func(arg1, arg2)
	callback()
# 注意 @return_future 和 @gen.engine可以被应用到同一个方法，提供的 @return_future第一个出现.
# 然而，解释器使用 @gen.coroutine代替这个组合.

# tornado.concurrent.chain_future(a, b)
# 链接两个futures到一起，这样当一个结束时，另一个也结束.
# a 的结果(成功或失败)会被复制到 b，除非在a完成的时候 b已经被结束或取消.