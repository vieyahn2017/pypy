import pecan

from lightrest import config
from lightrest.hooks import httphooks


def get_pecan_config():
    filename = config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [httphooks.ConfigHook(pecan_config),
                 httphooks.ContextHook()]
    pecan.configuration.set_config(dict(pecan_config), overwrite=True)
    app = pecan.make_app(
        pecan_config.app.applications[pecan_config.app.app_switch],
        debug=pecan_config.app.debug,
        hooks=app_hooks, logging=getattr(pecan_config, 'logging', {}),)
    return app


class VersionSelectorApplication(object):
    def __init__(self):
        self.pc = get_pecan_config()
        self.app = setup_app(pecan_config=self.pc)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
