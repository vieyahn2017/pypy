#-*- coding:utf-8 -*-
from setuptools import setup, find_packages
import sys
reload(sys)
sys.setdefaultencoding('gb18030')

setup(
    name = "OpenStackPythonSdk",
    version="1.0.0",
    packages = find_packages(),
    zip_safe = False,

    description = "OpenStack Python SDK",
    long_description = "Huawei IT Python SDK",
    author = "huawei",
    author_email = "zhuzhihua@huawei.com",
    install_requires = [
        'pbr<2.0,>=1.6',
        'argparse',
        'PrettyTable<0.8,>=0.7',
        'requests!=2.8.0,>=2.5.2',
        'warlock<2,>=1.0.1',
        'Babel>=1.3',
        'iso8601>=0.1.9',
        'six>=1.9.0',
        'oslo.utils>=2.8.0',
        'oslo.i18n>=1.5.0',
        'debtcollector>=0.3.0',
        'netaddr',
        'oslo.config>=2.3.0',
        'oslo.serialization>=1.4.0',
        'stevedore>=1.5.0',
        'cliff',
        'simplejson',
        'keystoneauth1>=2.1.0',
        'netifaces'
         ],

    license = "GPL",
    keywords = ("test", "egg"),
    platforms = "Independant"
)
