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


class TextSearch(BaseSearch):
    implements(ISearchableColumn)

    searchabletext_index_template = ViewPageTemplateFile('templates/searchabletext_index_string.pt')
    field_index_template = ViewPageTemplateFile('templates/field_index_string.pt')
    
    def index_values(self):
        tp_catalog = getToolByName(self.context, 'tablepage_catalog')
        return tp_catalog.uniqueValuesFor(self.id)

    def render(self, meta_type):
        if meta_type=='FieldIndex':
            return self.field_index_template(id=self.id,
                                             label=self.label,
                                             description=self.description)
        return self.searchabletext_index_template(id=self.id,
                                                  label=self.label,
                                                  description=self.description)
