# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.fields.base import BaseField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class TextField(BaseField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/string.pt')
    view_template = ViewPageTemplateFile('templates/string_view.pt')


class TextAreaField(BaseField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/textarea.pt')
    view_template = ViewPageTemplateFile('templates/textarea_view.pt')

    def renderText(self, text):
        context = self.context
        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo('text/html', text,
                                     context=context,
                                     mimetype='text/plain')
        return data.getData()
