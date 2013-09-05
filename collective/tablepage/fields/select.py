# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.fields.base import BaseField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class SelectField(BaseField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/select.pt')
    view_template = ViewPageTemplateFile('templates/string_view.pt')

    def vocabulary(self):
        raw_vocabulary = self.configuration['vocabulary']
        return raw_vocabulary.rstrip().splitlines()

