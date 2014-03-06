# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.fields.computed.interfaces import IComputedColumnHandler


class BaseHandler(object):
    """Base implementation: just return the stored data"""
    implements(IComputedColumnHandler)
    
    def __init__(self, column):
        self.column = column
    
    def __call__(self, data):
        return data
