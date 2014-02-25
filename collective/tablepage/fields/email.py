# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.fields.interfaces import IEmailColumnField
from collective.tablepage.fields.text import TextField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class EmailField(TextField):
    implements(IEmailColumnField)

    edit_template = ViewPageTemplateFile('templates/email.pt')
    view_template = ViewPageTemplateFile('templates/email_view.pt')

