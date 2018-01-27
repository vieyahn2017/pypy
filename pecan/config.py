# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'applications': {
        'generic': 'lightrest.controllers.generic.RootController',
        'rest': 'lightrest.controllers.rest.RootController',
        'advanced': 'lightrest.controllers.advanced.RootController'},
    'modules': ['lightrest'],
    'static_root': '%(confdir)s/public',
    'debug': True,
    'app_switch': 'advanced'
}

logging = {
    'root': {'level': 'DEBUG', 'handlers': ['console']},
    'loggers': {
        'lightrest': {'level': 'DEBUG', 'handlers': ['console']},
        'pecan': {'level': 'DEBUG', 'handlers': ['console']},
        'py.warnings': {'handlers': ['console']},
        '__force_dict__': True
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        },
        'color': {
            '()': 'pecan.log.ColorFormatter',
            'format': ('%(asctime)s [%(padded_color_levelname)s] [%(name)s]'
                       '[%(threadName)s] %(message)s'),
        '__force_dict__': True
        }
    }
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf

wsme = {
    'debug': True
}
