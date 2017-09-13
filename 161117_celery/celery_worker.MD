D:\python\single>celery worker -A celery_config -l info -c 5
[2016-11-17 15:49:32,681: WARNING/MainProcess] c:\python27\lib\site-packages\cel
ery\apps\worker.py:161: CDeprecationWarning:
Starting from version 3.2 Celery will refuse to accept pickle by default.

The pickle serializer is a security concern as it may give attackers
the ability to execute any command.  It's important to secure
your broker from unauthorized access when using pickle, so we think
that enabling pickle should require a deliberate action and not be
the default choice.

If you depend on pickle then you should set a setting to disable this
warning and to be sure that everything will continue working
when you upgrade to Celery 3.2::

    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

You must only enable the serializers that you will actually use.


  warnings.warn(CDeprecationWarning(W_PICKLE_DEPRECATED))

 -------------- celery@WIN-20150824SAC v3.1.25 (Cipater)
---- **** -----
--- * ***  * -- Windows-7-6.1.7601-SP1
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         celery_config:0x419d2e8
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 5 (prefork)
-- ******* ----
--- ***** ----- [queues]
 -------------- .> celery           exchange=celery(direct) key=celery


[tasks]
  . celery_add.add
  . celery_blog.fetch_url
  . celery_crawl.crawl

[2016-11-17 15:49:33,558: INFO/MainProcess] Connected to redis://localhost:6379/
0
[2016-11-17 15:49:33,598: INFO/MainProcess] mingle: searching for neighbors
[2016-11-17 15:49:34,665: INFO/MainProcess] mingle: all alone
[2016-11-17 15:49:34,828: WARNING/MainProcess] celery@WIN-20150824SAC ready.
[2016-11-17 15:49:36,562: INFO/MainProcess] Received task: celery_crawl.crawl[2d
6d2ce0-2292-4cdc-a468-d9391932a50b]
[2016-11-17 15:49:36,698: INFO/Worker-1] Starting new HTTP connection (1): bigda
ta.51cto.com
[2016-11-17 15:49:37,095: ERROR/MainProcess] Task celery_crawl.crawl[2d6d2ce0-22
92-4cdc-a468-d9391932a50b] raised unexpected: UnicodeEncodeError('ascii', u'\u04
bb\ufffd\u0774\ufffd\ufffd\ufffd\ufffd\ufffd\u0378\xa9\ufffd\u02f8\ufffd\ufffd\u
D:\python\single>celery worker -A celery_config -l info -c 5
[2016-11-17 15:51:30,907: WARNING/MainProcess] c:\python27\lib\site-packages\cel
ery\apps\worker.py:161: CDeprecationWarning:
Starting from version 3.2 Celery will refuse to accept pickle by default.

The pickle serializer is a security concern as it may give attackers
the ability to execute any command.  It's important to secure
your broker from unauthorized access when using pickle, so we think
that enabling pickle should require a deliberate action and not be
the default choice.

If you depend on pickle then you should set a setting to disable this
warning and to be sure that everything will continue working
when you upgrade to Celery 3.2::

    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

You must only enable the serializers that you will actually use.


  warnings.warn(CDeprecationWarning(W_PICKLE_DEPRECATED))

 -------------- celery@WIN-20150824SAC v3.1.25 (Cipater)
---- **** -----
--- * ***  * -- Windows-7-6.1.7601-SP1
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         celery_config:0x443d2e8
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 5 (prefork)
-- ******* ----
--- ***** ----- [queues]
 -------------- .> celery           exchange=celery(direct) key=celery


[tasks]
  . celery_add.add
  . celery_blog.fetch_url
  . celery_crawl.crawl

[2016-11-17 15:51:31,888: INFO/MainProcess] Connected to redis://localhost:6379/
0
[2016-11-17 15:51:31,930: INFO/MainProcess] mingle: searching for neighbors
[2016-11-17 15:51:32,944: INFO/MainProcess] mingle: all alone
[2016-11-17 15:51:33,253: WARNING/MainProcess] celery@WIN-20150824SAC ready.
[2016-11-17 15:51:37,134: INFO/MainProcess] Received task: celery_crawl.crawl[e3
dc8367-0d6b-4e10-b3ad-d73e9b8a5356]
[2016-11-17 15:51:37,165: INFO/Worker-1] Starting new HTTP connection (1): bigda
ta.51cto.com
[2016-11-17 15:51:37,385: WARNING/Worker-1] 2016-11-16 13:17:29
[2016-11-17 15:51:37,387: WARNING/Worker-1] 2016-11-15 15:10:07
[2016-11-17 15:51:37,388: WARNING/Worker-1] 2016-11-15 14:31:31
[2016-11-17 15:51:37,388: WARNING/Worker-1] 2016-11-15 11:10:11
[2016-11-17 15:51:37,390: WARNING/Worker-1] 2016-11-16 09:12:16
[2016-11-17 15:51:37,390: WARNING/Worker-1] 2016-11-15 10:32:35
[2016-11-17 15:51:37,391: WARNING/Worker-1] 2016-11-15 09:54:19
[2016-11-17 15:51:37,400: INFO/MainProcess] Task celery_crawl.crawl[e3dc8367-0d6
b-4e10-b3ad-d73e9b8a5356] succeeded in 0.259000062943s: None
[2016-11-17 15:52:25,522: INFO/MainProcess] Received task: celery_add.add[b9a1d2
de-6b9b-4912-8ee2-5d4cbb6b8592]
[2016-11-17 15:52:25,542: INFO/MainProcess] Task celery_add.add[b9a1d2de-6b9b-49
12-8ee2-5d4cbb6b8592] succeeded in 0.018000125885s: 233228
[2016-11-17 15:52:36,578: INFO/MainProcess] Received task: celery_add.add[3ac2b6
d8-7df4-4042-90d1-6380292636c2]
[2016-11-17 15:52:36,585: ERROR/MainProcess] Task celery_add.add[3ac2b6d8-7df4-4
042-90d1-6380292636c2] raised unexpected: TypeError('add() takes exactly 2 argum
ents (1 given)',)
Traceback (most recent call last):
  File "c:\python27\lib\site-packages\celery\app\trace.py", line 240, in trace_t
ask
    R = retval = fun(*args, **kwargs)
  File "c:\python27\lib\site-packages\celery\app\trace.py", line 438, in __prote
cted_call__
    return self.run(*args, **kwargs)
TypeError: add() takes exactly 2 arguments (1 given)
[2016-11-17 15:52:49,069: INFO/MainProcess] Received task: celery_add.add[1ee4da
54-a0ed-47af-a096-f2a81071596f]
[2016-11-17 15:52:49,076: INFO/MainProcess] Task celery_add.add[1ee4da54-a0ed-47
af-a096-f2a81071596f] succeeded in 0.00499987602234s: 3322332ewwwwwwwwwwww
[2016-11-17 15:59:23,907: INFO/MainProcess] Received task: celery_add.add[8b8e52
f9-264f-46ab-b8c7-6ebb63376702]
[2016-11-17 15:59:23,926: INFO/MainProcess] Task celery_add.add[8b8e52f9-264f-46
ab-b8c7-6ebb63376702] succeeded in 0.0110001564026s: 3322332ewwwwwwwwwwww
