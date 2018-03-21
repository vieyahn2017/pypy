from pecan import expose


class NodeController(object):
    @expose(template='json')
    def index(self):
        # /node/index
        return {'result': 'Call the method named index'}

    @expose(template='json')
    def post(self, **kwargs):
        # /node/post
        return {'body': kwargs}

    @expose(template='json')
    def put(self, nodeid, **kwargs):
        # /node/put
        return {'body': kwargs, 'id': nodeid}

    @expose(template='json')
    def delete(self, nodeid):
        # /node/delete
        return {'result': 'Call the method named delete'}


class VersionController(object):
    @expose(template='json')
    def _default(self):
        return {'Version': 'v1.0'}


class RootController(object):
    node = NodeController()
    version = VersionController()
