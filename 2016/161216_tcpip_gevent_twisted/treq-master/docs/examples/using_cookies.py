from twisted.internet.task import react
from _utils import print_response

import treq


def main(reactor, *args):
    d = treq.get('http://httpbin.org/cookies/set?hello=world')

    def _get_jar(resp):
        jar = resp.cookies()

        print 'The server set our hello cookie to: {0}'.format(jar['hello'])

        return treq.get('http://httpbin.org/cookies', cookies=jar)

    d.addCallback(_get_jar)
    d.addCallback(print_response)

    return d

react(main, [])
