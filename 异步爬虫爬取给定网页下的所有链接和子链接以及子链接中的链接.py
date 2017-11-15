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
