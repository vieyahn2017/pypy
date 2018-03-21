import json
import six
from wsme import types as wtypes

from lightrest.common import exceptions
from lightrest.common import utils


class UuidType(wtypes.UserType):

    basetype = wtypes.text
    name = 'uuid'

    @staticmethod
    def validate(value):
        if not utils.is_uuid_like(value):
            raise exceptions.InvalidUUID(uuid=value)
        return value

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return UuidType.validate(value)


class BooleanType(wtypes.UserType):
    """A simple boolean type."""

    basetype = wtypes.text
    name = 'boolean'

    @staticmethod
    def validate(value):
        try:
            return utils.bool_from_string(value, strict=True)
        except ValueError as e:
            raise exceptions.Invalid(e)

    @staticmethod
    def frombasetype(value):
        if value is None:
            return None
        return BooleanType.validate(value)


class JsonType(wtypes.UserType):

    basetype = wtypes.text
    name = 'json'

    def __str__(self):
        # These are the json serializable native types
        return ' | '.join(map(str, (wtypes.text, six.integer_types, float,
                                    BooleanType, list, dict, None)))

    @staticmethod
    def validate(value):
        try:
            json.dumps(value)
        except TypeError as e:
            raise exceptions.Invalid(e)
        else:
            return value

    @staticmethod
    def frombasetype(value):
        return JsonType.validate(value)

jsontype = JsonType()
booleantype = BooleanType()
uuidtype = UuidType()
