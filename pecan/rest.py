import json
from pecan import expose
from pecan import rest
from pecan import response
import six
from six.moves import http_client
from webob import exc


class NodeNicController(rest.RestController):

    @expose(template='json')
    def post(self, nodeid, **body):
        return {'class': body}


class NodeController(rest.RestController):

    nic = NodeNicController()
    _custom_actions = {
        'start': ['POST'],
        'power-off': ['POST']
    }

    @expose(template='json')
    def get_all(self):
        return {'result': 'Call the method named get_all'}

    @expose(template='json')
    def get(self, nodeid):
        return {'result': 'Call the method named get', 'id': nodeid}

    @expose(template='json')
    def post(self, **body):
        response.status = http_client.ACCEPTED
        return {'node': body, 'method': 'post'}

    @expose(template='json')
    def put(self, nodeid, **body):
        response.status = http_client.ACCEPTED
        return {'body': body, 'id': nodeid}

    @expose(template='json')
    def delete(self, nodeid):
        response.status = http_client.NO_CONTENT
        return {'result': 'Call the method named delete', 'id': nodeid}

    @expose(template='json')
    def start(self, nodeid):
        response.status = http_client.ACCEPTED
        return {'result': 'Call the method named start', 'id': nodeid}

    def power_off(self, nodeid):
        response.status = http_client.ACCEPTED
        return {'result': 'Call the method named power_off', 'id': nodeid}


setattr(NodeController, 'power-operate',
        expose(template='json')(
            six.get_method_function(NodeController.power_operate)))


class VersionController(rest.RestController):

    @expose(template='json')
    def _default(self):
        return {'Version': 'v1.0'}


class RootController(rest.RestController):
    node = NodeController()
    version = VersionController()

    @expose()
    def _route(self, args, request):
        if request.content_type != 'application/json':
            raise exc.HTTPBadRequest('Not support content-type')
        return super(RootController, self)._route(args, request)
