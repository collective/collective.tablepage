# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.search.interfaces import ISearchableColumn

class TextSearch(object):
    implements(ISearchableColumn)

    def __init__(self, context, request):
        self.context = context
        self.request = request
