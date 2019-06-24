"""mindlogger_build_applet - build your mindlogger survey in python"""

__version__ = '0.1.0'
__author__ = 'akeshavan <anishakeshavan@gmail.com>'
__all__ = []

from .item import Radio

def radio_item():
    print('todo radio')

def slider_item():
    print('todo slider')

def build_activity():
    raise NotImplementedError()

def build_applet():
    raise NotImplementedError()

