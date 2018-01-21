from datetime import datetime
import pecan
from pecan import expose
from pecan import rest
import six
from six.moves import http_client
import uuid
from webob import exc
import wsme
from wsmeext.pecan import wsexpose
from wsme import types as wtypes

from lightrest.common import datatypes
from lightrest.common import utils


class Node(wtypes.Base):

    name = wsme.wsattr(wtypes.text, mandatory=True)
    uuid = wsme.wsattr(datatypes.uuidtype, readonly=True)
    console_enabled = datatypes.booleantype
    power_state = wsme.wsattr(
        wtypes.Enum(str, 'power-on', 'power-off'), mandatory=True)
    raid_config = wsme.wsattr({wtypes.text: datatypes.jsontype})
    disks = [wtypes.text]
    update_time = datetime

    _classis_uuid = None

    def _get_classis_uuid(self):
        return self._classis_uuid

    def _set_classis_uuid(self, value):
        if value:
            self._classis_uuid = value
        elif value == wtypes.Unset:
            self._classis_uuid = wtypes.Unset

    classis_uuid = wsme.wsproperty(datatypes.uuidtype, _get_classis_uuid,
                                   _set_classis_uuid)


class NodeRequest(wtypes.Base):
    node = wsme.wsattr(Node, mandatory=True)


class PowerRequest(wtypes.Base):
    power_action = wsme.wsattr(
        wtypes.Enum(str, 'power-on', 'power-off'), mandatory=True)


class NodeController(rest.RestController):

    _custom_actions = {
        'power-operate': ['POST'],
        'start': ['GET']
    }

    @wsexpose(Node, datatypes.uuidtype, wtypes.text,
              datatypes.uuidtype, int, int, bool)
    def get(self, nodeid, name=None, uuid=None,
            page=None, limit=None, show_all=False):
        node = Node()
        node.name = 'node1'
        node.console_enabled = True
        node.power_state = 'power-on'
        node.raid_config = dict(name='lucifer')
        node.disks = ['/dev/sda', '/dev/sdb']
        return node

    @wsexpose([Node])
    def get_all(self):
        print pecan.request.cfg.server
        print pecan.request.cfg.server.host
        print pecan.request.cfg.server.port
        node = Node()
        node.name = 'node1'
        node.console_enabled = True
        node.power_state = 'power-on'
        node.raid_config = dict(name='lucifer')
        node.disks = ['/dev/sda', '/dev/sdb']
        node.update_time = datetime.now()
        return [node]

    @wsexpose(None, datatypes.uuidtype, status_code=http_client.NO_CONTENT)
    def delete(self, nodeid):
        return {'result': 'Call the method named delete'}

    @wsexpose(Node, body=NodeRequest, status_code=http_client.CREATED)
    def post(self, nodereq):
        node = nodereq.node
        node.uuid = uuid.uuid4().hex
        return node

    @wsexpose(Node, datatypes.uuidtype, body=NodeRequest,
              status_code=http_client.ACCEPTED,
              rest_content_type=('json',))
    def put(self, nodeid, nodereq):
        node = nodereq.node
        node.uuid = nodeid
        return node

    @wsexpose(Node)
    def start(self):
        node = Node()
        node.name = 'node1'
        node.console_enabled = True
        node.power_state = 'power-on'
        node.raid_config = dict(name='lucifer')
        node.disks = ['/dev/sda', '/dev/sdb']
        node.update_time = datetime.now()
        return node

    def power_operate(self, nodeid, power_request):
        print power_request.power_action


setattr(NodeController, 'power-operate',
        wsexpose(None, datatypes.uuidtype, body=PowerRequest,
                 status_code=http_client.ACCEPTED,
                 rest_content_type=('json',))(
                     six.get_method_function(NodeController.power_operate)))


class RootController(rest.RestController):
    node = NodeController()

    @expose()
    def _route(self, args, request):
        if len(args) <= 2 and not utils.is_uuid_like(args[0]):
            msg = 'UUID like Project id is required, and the url like follows'\
                  '/{project_id}/resources'
            raise exc.HTTPNotFound(msg)

        if args[0] != request.headers.get('X-Auth-Token'):
            raise exc.HTTPForbidden(
                'Has no access to visit the %s resources' % args[0])
        del args[0]
        return super(RootController, self)._route(args, request)
