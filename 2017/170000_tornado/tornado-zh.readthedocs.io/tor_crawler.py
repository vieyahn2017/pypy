# Queue
# Tornado的tornado.queue模块为基于协程的应用程序实现了一个异步生产者/消费者模式的队列。这与Python标准库为多线程环境实现的queue模块类似。
# 一个协程执行到yield queue.get会暂停，直到队列中有条目。如果queue有上限，一个协程执行yield queue.put将会暂停，直到队列中有空闲的位置。
# 在一个queue内部维护了一个未完成任务的引用计数，每调用一次put操作便会增加引用计数，而调用task_done操作将会减少引用计数。

# 下面是一个简单的web爬虫的例子：
# 最开始，queue只包含一个基准url。当一个worker从中取出一个url后，它会从对应的页面中解析中所包含的url并将其放入队列，然后调用task_done减少引用计数一次。
# 最后，worker会取出一个url，而这个url页面中的所有url都已经被处理过了，这时队列中也没有url了。这时调用task_done会将引用计数减少至0.
# 这样,在main协程里，join操作将会解除挂起并结束主协程。

# 这个爬虫使用了HTMLParse来解析html页面。




import time
from datetime import timedelta
try:
    from HTMLParser import HTMLParser
    from urlparse import urljoin, urldefrag
except ImportError:
    from html.parser import HTMLParser
    from urllib.parse import urljoin, urldefrag

from tornado import httpclient, gen, ioloop, queues

base_url = 'http://www.tornadoweb.org/en/stable/'
concurrency = 10

@gen.coroutine
def get_links_from_url(url):
    """Download the page at `url` and parse it for links.

    Returned links have had the fragment after `#` removed, and have been made
    absolute so, e.g. the URL 'gen.html#tornado.gen.coroutine' becomes
    'http://www.tornadoweb.org/en/stable/gen.html'.
    """
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(url)
        print('fetched %s' % url)

        html = response.body if isinstance(response.body, str) else response.body.decode()
        urls = [urljoin(url, remove_fragment(new_url)) for new_url in get_links(html)]
    except Exception as e:
        print('Exception: %s %s' % (e, url))
        raise gen.Return([])

    raise gen.Return(urls)


def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url

def get_links(html):
    class URLSeeker(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.urls = []

        def handle_starttag(self, tag, attrs):
            href = dict(attrs).get('href')
            if href and tag == 'a':
                self.urls.append(href)

    url_seeker = URLSeeker()
    url_seeker.feed(html)
    return url_seeker.urls

@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched = set(), set()

    @gen.coroutine
    def fetch_url():
        current_url = yield q.get()
        try:
            if current_url in fetching:
                return
            print('fetching %s' % current_url)
            fetching.add(current_url)
            urls = yield get_links_from_url(current_url)
            fetched.add(current_url)
            for new_url in urls:
                # Only follow links beneath the base URL
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
    yield q.join(timeout=timedelta(seconds=300))
    assert fetching == fetched
    print('Done in %d seconds, fetched %s URLs.' % (time.time() - start, len(fetched)))


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)