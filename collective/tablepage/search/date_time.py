# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from collective.tablepage.search.interfaces import ISearchableColumn
from collective.tablepage.search.base import BaseSearch

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class DateTimeSearch(BaseSearch):
    implements(ISearchableColumn)

    template = ViewPageTemplateFile('templates/datetime_index.pt')
    show_hm = True
    
    def render(self, meta_type):
        if meta_type=='DateIndex':
            return self.template(id=self.id,
                                 label=self.label,
                                 description=self.description)
        return ''


class DateSearch(DateTimeSearch):
    show_hm = False
