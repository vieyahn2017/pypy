import os
from wsgiref.simple_server import make_server

from lightrest import app


if __name__ == '__main__':
    wsgi_app = app.VersionSelectorApplication()
    listen_host = wsgi_app.pc.server.host
    listen_port = int(wsgi_app.pc.server.port)
    server = make_server(listen_host, listen_port, wsgi_app)
    server.serve_forever()
