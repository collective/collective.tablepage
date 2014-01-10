# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from collective.tablepage.fields.interfaces import INumberColumnField
from collective.tablepage.fields.text import TextField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class NumberField(TextField):
    implements(INumberColumnField)

    edit_template = ViewPageTemplateFile('templates/number.pt')

