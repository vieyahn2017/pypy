from pecan import hooks
from webob import exc

class ConfigHook(hooks.PecanHook):

    def __init__(self, cfg):
        self.cfg = cfg

    def before(self, state):
        state.request.cfg = self.cfg


class ContextHook(hooks.PecanHook):

    def before(self, state):
        pass

    def on_route(self, state):
        state.request.accept = 'application/json'

        if 'application/json' != state.request.content_type:
            raise exc.HTTPBadRequest('Not supported content-type')

        if not state.request.headers.get('X-Auth-Token'):
            raise exc.HTTPBadRequest(
                'X-Auth-Token is required in request headers')

    def after(self, state):
        pass
