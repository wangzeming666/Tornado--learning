# tornado.web_RequestHandler_And_ApplicationClass.py

# tornado.web 提供一个简单的异步web框架，这允许它扩展到大量的开放连接，使其成为长轮询的理想选择.
# 这是一个简单的 Hello, world 应用示例：
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Hello, world")

if __name__ == '__main__':
	application = tornado.web.Application([
		(r'/', MainHandler),
		])
	application.listen(8888)
	tornado.ioloop.IOLoop.current().start()

# 查看用户手册获取额外信息


# 线程安全笔记
# 一般，RequestHandler和Tornado其它位置中的方法都不是线程安全的. 特别的，诸如write(), finish(), flush() 方法
# 只能被主线程调用. 如果你使用多线程，必须使用IOLoop.add_callback，在请求结束前将控制权转回主线程.


# Request handlers

# class tornado.web.RequestHandler(application, request, **kwargs)
# HTTP请求处理的基础类.
# 子类必须定义-至少方法之一定义在'Entry points'(入口点)部分下.
# (Subclasses must define at least one of the methods defined in the "Entry points" section below.)

# Entry points(入口点)
# RequestHandler.initialize()
# 子类初始化的钩子. 被每个请求调用.
# 一个字典作为第三参数传递给url说明(url spec)，将会被作为关键字参数提供给initialize().
# 示例：
class Profilehandler(RequestHandler):
	def initialize(self, database):
		self.database = database

	def get(self, username):
		...

app = Application([
	(r'/user/(.*)', ProfileHandler, dict(database=database)),
	])

# RequestHandler.prepare()
# 在请求的最开始于get/post/etc之前被调用.
# 覆写这个方法执行常见的初始化，无论请求方法是什么.
# 异步支持：使用 gen.coroutine or return_future 装饰这个方法，来使它异步(asynchronous装饰器不能在prepare使用).
# 如果这个方法返回一个Future执行不会立即开始，直到Future完成.
# 3.1新版功能，异步支持.

# RequestHandler.on_finish()
# 在请求的最后被调用
# 覆写这个方法执行清除、记录等. 这个方法是一个prepare的副本. on_finish 可能不会产生任何输出，它可能在响应被送到客户端后调用.
# 执行任何下面的方法(众所周知的HTTP verb(动词)方法)去处理类似的HTTP方法.
# 这些方法可以被这些装饰器的任一制造异步：gen.coroutine, return_future, asynchronous.
# 覆写类变量来支持不在这个列表的变量 SUPPORTED_METHODS：
class WebDAVHandler(RequestHandler):
	SUPPORTED_METHODS = RequestHandler.SUPPORTED_METHODS + ('PROPFIND',)

	def propfind(self):
		pass

# RequestHandler.get(*args, **kwargs)

# RequestHandler.head(*args, **kwargs)

# RequestHandler.post(*args, **kwargs)

# RequestHandler.delete(*args, **kwargs)

# RequestHandler.patch(*args, **kwargs)

# RequestHandler.put(*args, **kwargs)

# RequestHandler.options(*args, **kwargs)


# Input
# RequestHandler.get_argument(name, default=<object object>, strip=True)
# 返回给定name的参数值
# 如果默认值没有被提供，参数被认为是被需要的，如果它不存在，我们抛出一个MissingArgumentError.
# 如果参数出现在url中超过一次，我们返回最后的值.
# 返回值总是unicode.

# RequestHandler.get_arguments(name, strip=True)        # 与上面不同是argument复数形式
# 返回一个给定name的参数列表.
# 如果参数不存在，返回一个空列表.
# 返回值是unicode.

# RequestHandler.get_query_argument(name, default=<object object>, strip=True)
# 返回请求问号字符串中给定name参数的值.
# 如果默认值没有被提供，参数被认为是必须的，如果没有给出会抛出一个MissingArgumentError.
# 如果参数在url中出现超过一次，返回最后一个值.
# 返回值unicode.
# 3.2新功能

# RequestHandler.get_query_arguments(name, strip=True)
# 返回一个给定name中问号参数的列表.
# 如果参数不存在，返回一个空列表.
# 返回值unicode.
# 3.2新功能

# RequestHandler.get_body_argument(name, default=<object object>, strip=True)
# 返回请求body中给定name的参数值.
# 如果默认值没有被提供，参数被认为是必须的，如果没有给出会抛出一个MissingArgumentError.
# 如果参数在url中出现超过一次，返回最后一个值.
# 返回值unicode.
# 3.2新功能

# RequestHandler.get_body_arguments(name, strip=True)
# 返回请求body中给定name的参数值列表.
# 如果参数不存在，返回一个空列表.
# 返回值unicode.
# 3.2新功能

# RequestHandler.decode_argument(value, name=None)
# 从请求中解码一个参数.
# 参数已经被percent-decode(百分比解码??)，现在是一个字节字符串. 默认情况下，这个方法以utf=8解码参数并返回一个unicode字符串，
# 但这可能被在子类中被覆写.
# 这个方法被用作一个过滤器，get_argument[s]() and 传递给(passed to) get()/post()/etc 中提取值，这些情况都可以使用.
# 如果知道，参数的名字被提供. 但是可能是None(例如url正则表达式中的未命名组).

# RequestHandler.request
# tornado.httputil.HTTPServerRequest 对象包含附加的请求参数包括例如headers and body data.

# RequestHandler.path_args

# RequestHandler.path_kwargs
# path_args 和 path_kwargs属性包含位置参数和关键字参数，被传递给HTTP verb methods.
# 这些属性在这些方法被调用之前被设置，所以值在prepare期间可以被获取.


# Output
# RequestHandler.set_status(status_code, reason=None)
# 设置响应状态码(status code)
# 参数：
# 		status_code(int)--状态响应码. 如果reason 是None，它必须出现在httplib.responses.
#       reason(string)--便于阅读的原因短语描述状态码. 如果 None，它会被httplib.responses 填满

# RequestHandler.set_header(name, value)
# 设置给定的响应 header name and value.
# 如果一个datetime被给出，我们自动的将它转化格式为HTTP规范. 如果值不是一个字符串，我们转化它为一个字符串. 所有的header值都以UTF-8编码.

# RequestHandler.set_default_headers()
# 在请求的开始覆写它来设置HTTP headers.
# 例如，这是设置自定义 server 头的地方. 注意，在请求处理的正常流程中设置这样的标头可能不符合您的要求，因为在错误处理过程中可能会重置标头.

# RequestHandler.write(chunk)
# 将给出的数据块写入输出缓冲区. 
# 要将输出写到网络，使用下一个flush()方法.
# 如果给定的数据块是一个字典，我们将其写为JSON，并将响应的内容类型设置为application/JSON(如果你想以一个不同的Content-Type发送JSON，
# 在调用write()后调用set_header).
# 注意列表不嫩恶搞被转换到JSON因为潜在跨站点的安全弱点. 所有的JSON输出应被包裹在字典中. 更多细节信息访问：
# http://haacked.com/archive/2009/06/25/json-hijacking.aspx/    and
# https://github.com/facebook/tornado(龙卷风)/issues/1009

# RequestHandler.flush(include_footers=False, callback=None)
# 将当前输出缓存冲入网络.
# (The callback argument, if given, cann be used for flow control: it will be run when all flushed data has been written
#  to the socket.)
# (Note that only one flush callback can be outstanding at a time; if another flush occurs before the previous flush's callback
# has been run, the previous callback will be discarded)
# 上述文字无法准确翻译，大致意思为：给出回调参数可以限制流量，它会在flushed数据被写入到socket之后执行. 同一时间只有一个flush回调呈现，新的
# flush如果发生在旧的flush回调运行前，旧的则会被抱起.

# RequestHandler.finish(chunk=None)
# 完成响应，结束HTTP请求.

# RequesHandler.on_finish(self)
# 定义这个方法会在程序结束时自动调用，它调用finish方法

# RequestHandler.render(template_name, **kwargs)
# 以给出的参数作为响应渲染模板.

# RequestHandler.render_string(template_name, **kwargs)
# 以给出的参数生成给定的模板.

# RequestHandler.get_template_namespace()
# 返回一个字典被用作默认模板命名空间.
# 可能会作为子类被覆写以添加或修改值.
# 此方法的结果会被与tornado.template模块中附带的默认值和关键字参数一并送到render or render_string.
# (The results of this method will be combined with additional defaults in the tornadol.template moudle
# and keyword arguments to render or render_string.)

# RequestHandler.redirect(url, permanent=False, status=None)
# 发送一个重定向到给定的URL(可选相对路径).
# 如果status 参数被指定，这个值被用作HTTP状态码；否则301(永久的)或302(临时的)任一被选中为permanent参数.
# 默认是302(临时的).

# RequestHandler.send_error(status_code=500, **kwargs)
# 发送给定的HTTP错误码到浏览器.
# 如果flush()已经被调用，错误不可能被送出，所以这个方法会简单的中止响应. 如果输出被写入但还没有flushed，它会被
# 抛弃并被错误页面取代.
# 覆写write_error()来自定义错误页面的返回. 附加关键字参数通过write_error被传递.

# RequestHandler.write_error(status_code, **kwargs)
# 覆写以实现定制错误页面.
# write_error可能调用write, render, set_header等像往常一样生产输出. 
# 如果这个错误被未捕获的异常引发(包括HTTPError)，一个exc_info triple(may be 三个参数)会以kwargs['exc_info']
# 被获取. 注意这个异常可能不是如sys.exc_info or traceback.format_exc方法想要的当前的异常.

# RequestHandler.clear()
# 为这次响应重新设定(reset)所有的headers和内容.

# RequestHandler.data_received(chunk)
# 实现这个方法去处理流出的请求数据.
# 需要 stream_request_body 装饰器




# Cookies

# RequestHandler.cookies
# self.request.cookies 的别名.

# RequestHandler.get_cookie(name, default=None)
# 以给出的name取得cookie的值或默认值.

# RequestHandler.set_cookie(name, value, domain=None, expires=None, path='/', expires_days=None, **kwargs)
# 以给定的选项设置给定的cookie name/value.
# 附加关键字参数被立即设置在Cookie.Morsel上. 查看http://docs.python.org/library/cookie.html#morsel-objects中可获取的属性.

# RequestHandler.clear_all_cookies(path='/', domain=None)
# 删除所有的cookies用户发送的请求.
# 查看clear_cookie获取更多有关路径和参数域信息.
# 在3.2版本更改，添加了path和domain参数

# RequestHandler.get_secure_cookie(name, value=None, max_age_days=31, min_version=None)
# 给定的cookie签名如果有效，返回它，否则不反回. (Return the given signed cookie if it validates, or None.)
# 解码的cookie值被作为字节字符串返回(不同于get_cookie).

# RequestHandler.get_secure_cookie_key_version(name, value=None)
# 返回安全的cookie签名密钥版本.
# 版本作为int返回.

# RequestHandler.set_secure_cookie(name, value, expires_days=30, version=None, **kwargs)
# 时间戳和签名cookie防止被伪造.
# 你必须在你的Application中指定cookie_secret设置使用这种方法. 这会有一个长的、随机的字节序列被用作HMAC秘密签名.
# 使用get_secure_cookie()方法阅读cookie设置.
# 注意expires_days参数设置cookie在浏览器中的生命周期，但是独立于max_age_days参数 to get_secure_cookie.
# 安全cookie可能包含任意的字节值，不只是unicode字符串(不同于正则cookies).
# 在版本3.2.1中改变：添加version参数. 引进了cookie版本2，并设置了默认值.

# tornado.web.MIN_SUPPORTED_SIGNED_VALUE_VERSION=1
# 最老的签署值版本被这个Tornado的版本支持.
# 签署值比这个版本老的不能被解码(decode).
# 在版本3.2.1更新.

# tornado.web.MAX_SUPPORTED_SIGNED_VALUE_VERSION=2
# 最新的签名值被这个Tornado的版本支持.
# 签署值比这个版本新的不能被解码.
# 3.2.1版本更新.

# tornado.web.DEFAULT_SIGNED_VALUE_VERSION=2
# 签署值版本由RequestHandler.create_signed_value创建.
# 可以传递一个version关键字参数覆写.
# 3.2.1版本新增.

# tornado.web.DEFAULT_SIGNED_VALUE_MIN_VERSION=1
# 最老的签名值由RequestHandler.get_secure_cookie接受.
# 可以通过传递一个min_version关键字参数来覆写.
# 3.2.1版本新增.


# Other

# RequestHandler.application
# Application对象服务这个请求.

# RequestHandler.check_etag_header()
# 检查Etag header防止请求的If-None-Match.
# 如果请求的Etag匹配返回True并返回一个304
# e.g.
self.set_etag_header()
if self.check_etag_header():
	self.set_status(304)
	return
# 这个方法在请求完成时被自动调用，但可以更早的被调用给applications，覆盖compute_etag并想在请求完成前去
# 做一个早期的If-None-Match检查. Etag header 应被设置(也许与set_etag_header)在调用这个方法前.
# (This method is called automatically when the request is finished, but may be called earlier for 
# applications that override compute_etag and want to do an early check for If-None-Match before 
# completing the request. The Etag header should be set (perhaps with set_etag_header) before calling
#  this method.)

# (Etag(百度解释):
# HTTP协议规格说明定义ETag为“被请求变量的实体值”。另一种说法是，ETag是一个可以与Web资源关联的记号（token）.
# 典型的Web资源可以一个Web页，但也可能是JSON或XML文档。服务器单独负责判断记号是什么及其含义，并在HTTP响应头中
# 将其传送到客户端，以下是服务器端返回的格式：ETag:"50b1c1d4f775c61:df3"客户端的查询更新格式是这样的：
# If-None-Match : W / "50b1c1d4f775c61:df3"如果ETag没改变，则返回状态304然后不返回，这也和Last-Modified一样.
# 测试Etag主要在断点下载时比较有用.)

# RequestHandler.check_xsrf_cookie()
# 核实 _xsrf cookie匹配 _xsrf参数.
# 为防止跨站点请求伪造，我们设置一个_xsrf cookie并包含所有POST请求的非cookie字段的相同值.
# 如果两个值不匹配，我们以潜在的伪造为因拒绝表单提交.
# _xsrf值可能被设置为名为_xsrf的表单字段或在一个名为 X-XSRFToken or X-CSRFToken 的自定义HTTP header中(X-CSRFToken
# 可能兼容性更好??). 查看http://en.wikipedia.org/wiki/Cross-site_request_forgery.
# 之前的1.11发布，如果HTTP header X-Requested-With: XMLHTTPRequest 出现，这个检查被忽略.
# 这个异常已经被证明不安全并被移除. 更多信息查看 http://www.djangoproject.com/weblog/2011/feb/08/security/ 
# http://weblog.rubyonrails.org/2011/2/8/csrf-protection-bypass-in-ruby-on-rails
# 在3.2.2版本改变：加入cookie 版本2的支持. 现在版本1 和版本2 都可以支持了.

# RequestHandler.compute_etag()
# 计算etag header 以被这次请求使用.
# 默认使用hash内容书写. 
# 可以被覆写提供自定义etag实现，或可以返回None以禁用tornado的默认etag支持.

# RequestHandler.create_template_loader(template_path)
# 加载给出的路径，返回一个新的模板.
# 可以作为子类被覆写. 使用 autoescape和 template_whitespace application settings,
# 默认返回一个以给定路径的基于目录的加载(returns a directory-based loader on the given path).
# 如果一个template_loader application setting 被提供，则使用它代替.

# RequestHandler.current_user
# 此次请求用户认证.
# 这是两种设置方法中的一种：
# 一个子类可以覆写get_current_user(), 它会被自动调用，其中第一次被调用时self.current_user被访问(A subclass 
# may override get_current_user(), which will be called automatically the first time self.current_user
#  is accessed.).
# 每次请求get_current_user()只会被调用一次，并被缓存给future访问:
def get_current_user(self):
	user_cookie = self.get_secure_cookie('user')
	if user_cookie:
		return json.loads(user_cookie)
	return None
# 它可以被设置为一个常量，通常来自一个被覆写的prepare():
@gen.coroutine
def prepare(self):
	user_id_cookie = self.get_secure_cookie("user_id")
	if user_id_cookie:
		self.current_user = yield load_user(user_id_cookie)
# 注意当get_current_user()可能不存在时，prepare()可能是一个协程(Note that prepare() may be a coroutine while
# get_current_user() may not), 所以如果加载用户需要异步的操作，后面的形式是必须的.
# 用户对象可以是任何application的选择.

# RequestHandler.get_browser_locale(default='en_US')
# 从Accept-Language header确定user的区域.
# 查看 http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4

# RequestHandler.get_current_user()
# 覆写以确定当前用户，例如一个cookie.
# 这个方法可能不是一个协程.

# RequestHandler.get_login_url()
# 覆写以根据请求自定义登录URL.
# 默认情况下，我们使用login_url 应用设置.

# RequestHandler.get_status()
# 返回响应的状态码.

# RequestHandler.get_template_path()
# 覆写以为每次处理自定义模板路径. 
# 默认情况下，我们使用template_path 应用设置. 返回None去加载相路径对于调用文件路的模板.

# RequestHandler.get_user_locale()
# 覆写以从已认证用户确定区域(locale).
# 这个方法应返回一个tornado.locale.Locale对象，最有可能通过调用像tornado.locale.get("en")来获得.

# RequestHandler.locale
# 当前session的区域.
# 要么以get_user_locale确定，你可以覆写它设置locale，例如存储在数据库中的一个用户偏好，要么以get_browser_locale
# 确定，它使用Accept-Language header.

# RequestHandler.log_exception(typ, value, tb)
# 覆写以自定义未捕获异常的记录.
# 默认情况记录HTTPError的示例作为警告而不是记录堆栈跟踪(在tornado.general记录器上)，所有其它异常错误堆栈跟踪(
# on the tornado.general 记录器).
# 3.1版本新增.

# RequestHandler.on_connection_close()
# 在异步处理中如果客户端关闭连接，则调用.
# 覆写这个去清空长连接的相关资源. 注意这个方法被仅在异步进程结束连接时调用; 如果你需要在每个请求后做清空工作，
# 使用 on_finish代替.
# 代理可能会在客户端退出后仍保持连接开放一段时间(并不一定会)，所以这个方法在用户关闭他们的连接结束后，可能
# 不被立即调用.

# RequestHandler.require_setting(name, feature='this feature')
# 如果给定的app setting 没有被定义，抛出一个异常.

# RequestHandler.reverse_url(name, *args)
# Application.reverse_url的别名.

# RequestHandler.set_etag_header()
# 使用self.compute_etag()设置响应的Etag头.
# 注意，如果self.etag()返回None，不会有header被设置.
# 在请求完成时这个方法被自动调用.

# RequestHandler.settings
# 一个self.application.settings的别名.

# RequestHandler.static_url(path, include_host=None, **kwargs)
# 以给出的静态文件相对路径返回静态URL.
# 这个方法请求你在你的application中设置static_path设置(它指定你的静态文件根目录).
# 这个方法返回一个版本的url((a versioned url)默认添加?v=<signature>)，它允许静态文件无限期缓存.
# 这可以通过传递include_version=False(在默认的实现；其他静态文件实现不需要支持它，但他们可能支持
# 其他设定). 默认这个方法返回URLs相对路径到当前主机, 但是如果include_host是true则返回绝对路径.(
# By default this method returns URLs relative to the current host, but if include_host is true
# the URL returned will be absolute.)
# 如果这个handler有一个include_host属性，这个值会被用作默认值给所有的static_url调用，include_host
# 不会作为关键字参数被传递.
