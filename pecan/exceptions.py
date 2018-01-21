import six
from six.moves import http_client


class BaseException(Exception):
    _msg_fmt = "An unknown exception occurred."
    code = http_client.INTERNAL_SERVER_ERROR
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self._msg_fmt % kwargs

            except Exception as e:
                for name, value in kwargs.items():
                    raise e
                else:
                    message = self._msg_fmt

        super(BaseException, self).__init__(message)

    def __str__(self):
        """Encode to utf-8 then wsme api can consume it as well."""
        if not six.PY3:
            return unicode(self.args[0]).encode('utf-8')

        return self.args[0]

    def __unicode__(self):
        """Return a unicode representation of the exception message."""
        return unicode(self.args[0])


class Invalid(BaseException):
    _msg_fmt = "Unacceptable parameters."
    code = http_client.BAD_REQUEST


class InvalidUUID(Invalid):
    _msg_fmt = "Expected a uuid but received %(uuid)s."
