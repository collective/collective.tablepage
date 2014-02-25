# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from collective.tablepage.fields.interfaces import ITextColumnField
from collective.tablepage.fields.interfaces import ITextAreaColumnField
from collective.tablepage.fields.base import BaseField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class TextField(BaseField):
    implements(ITextColumnField)

    edit_template = ViewPageTemplateFile('templates/string.pt')
    view_template = ViewPageTemplateFile('templates/string_view.pt')


class TextAreaField(BaseField):
    implements(ITextAreaColumnField)

    edit_template = ViewPageTemplateFile('templates/textarea.pt')
    view_template = ViewPageTemplateFile('templates/textarea_view.pt')
    # we cache because we have portal_transforms but we can cache for a long time
    cache_time =  60 * 60 * 12 # 12 hours

    def __init__(self, context, request):
        BaseField.__init__(self, context, request)
        self.rows = 5

    def renderText(self, text):
        context = self.context
        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo('text/html', text, context=context,
                                     mimetype='text/plain')
        return data.getData()
