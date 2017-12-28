# -*- coding: utf-8 -*-

from collective.tablepage.browser.table import TableViewView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class MultipleTablesView(TableViewView):
    """View with multiple tables"""
    implements(IViewView)

    def __call__(self):
        return self.index()

    def is_label(self, row):
        return isinstance(row, basestring) and row or None

    def getHeader(self, col_index):
        return self.headers()[col_index]
