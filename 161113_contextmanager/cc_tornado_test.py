# -*- coding: utf-8 -*- 

from contextlib import contextmanager

class ClientPoolEmptyOnWindows(object):
    """only used fow windows not Error.  yanghao.8.31"""
    def get_stats(self):
        return 1

    @contextmanager
    def reserve(self):
        try:
            yield iter('abcdefg')
        finally:
            print('abcdefg!')

def getmc():
    """
    @return: Memcached ClientPool. 由于pylibmc不支持windows，为了适配代码，写的上面那个ClientPoolEmptyOnWindows
    """
    try:
        from pylibmc import Client, ClientPool
        cacheServers = ["10.0.0.252:11211"]
        MC_POOL_SIZE = 100
        adv_setting = {"cas": True, "tcp_nodelay": True, "ketama": True}
        mc = Client(cacheServers, binary=True, behaviors=adv_setting)
        return ClientPool(mc, MC_POOL_SIZE)
    except ImportError:
        return ClientPoolEmptyOnWindows()


context = {}
context['mc'] = getmc()

class StoreCache(object):
    def __init__(self):
        self._store = None

    def __enter__(self):
        try:
            with context['mc'].reserve() as mc:
                self._store = mc
        except:
            raise
        print self._store  # <iterator object at 0x0000000002CD9630>
        return self._store

    def __exit__(self, exc_type, exc_value, traceback):
        pass




class BaseHandler(object):

    @property
    def cache_server(self):
        with StoreCache() as mc:
            return mc


def test_mc():
    client = getmc()
    print client
    print client.get_stats()
    print client.reserve()



def main():
    test_mc()

    handler = BaseHandler()
    cache_server = handler.cache_server
    print cache_server




main()