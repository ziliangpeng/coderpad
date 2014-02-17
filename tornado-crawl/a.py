from tornado.httpclient import *
from tornado import ioloop
from threading import Lock
from Queue import Queue
import datetime

remain_task = 0
l = Lock()
q = Queue()

def handle_request(response):
    with l:
        global remain_task
        if response.error:
            if response.error.code == 599:
                http_client.fetch(response.request.url, handle_request)
                print 'retry', response.request.url
            elif response.error.code == 404:
                #print response.request.url,
                #print "Error:", response.error
                remain_task -= 1
            else:
                print response.request.url,
                print 'Error', response.error
                remain_task -= 1
        else:
            print response.request.url,
            print 'OK',
            filename = response.request.url[-6:]
            f = open(filename + '.txt', 'w')
            f.write(response.body)
            f.close()
            remain_task -= 1
            print 'remain', remain_task + q.qsize(),
            print datetime.datetime.now() - start_time,
            if '5dde501906b4898b284e8bde7b2bbd76.png' in response.body:
                print 'SQUARE',

            print ''


        if not q.empty():
            url = q.get()
            http_client.fetch(url, handle_request)
            remain_task += 1

        if remain_task == 0:
            io_loop.stop()
        #print 'remain', remain_task

http_client = AsyncHTTPClient()

for a in range(555555, 1000000):
    url = 'https://coderpad.io/' + '%06d' % a
    q.put(url)

for _ in range(500):
    if q.empty():
        break
    url = q.get()
    http_client.fetch(url, handle_request)
    remain_task += 1

start_time = datetime.datetime.now()
io_loop = ioloop.IOLoop.instance()
io_loop.start()
