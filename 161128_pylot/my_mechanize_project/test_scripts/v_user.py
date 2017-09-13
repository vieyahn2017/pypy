
import random
import time
import mechanize

class Transaction(object):
    def __init__(self):
        self.custom_timers = {}

    def run(self):
        br = mechanize.Browser()
        br.set_handle_robots(False)

        start_timer = time.time()
        resp = br.open('http://127.0.0.1:8888/')
        resp.read()
        latency = time.time() - start_timer

        self.custom_timers['Example_Homepage'] = latency

        assert (resp.code == 200), 'Bad HTTP Response'
        assert ('OK' in resp.get_data()), 'Failed Content Verification'    	



if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
