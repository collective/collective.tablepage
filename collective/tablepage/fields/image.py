# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from Acquisition import aq_inner, aq_parent
from Products.ATContentTypes.permission import permissions
from Products.CMFCore.utils import getToolByName
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.interfaces import IImageColumnField
from collective.tablepage.fields.interfaces import IMultiFileColumnField
from collective.tablepage.fields.link import LinkedObjectFinder
from collective.tablepage.interfaces import IColumnDataRetriever
from plone.memoize.instance import memoize
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import implements
from .file import FileField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

TYPE_TO_CREATE = 'Image'


class ImageField(FileField):
    implements(IImageColumnField)
    portal_type = TYPE_TO_CREATE

    edit_template = ViewPageTemplateFile('templates/image.pt')
    view_template = ViewPageTemplateFile('templates/image_view.pt')

    def _getCustomPreferences(self):
        """Override some preferences when displaying the linkable content
        @size will override image size displayed
        """
        prefs = super(ImageField, self)._getCustomPreferences()
        conf = self.configuration.get('vocabulary') or ''
        for c in conf.splitlines():
            if c.startswith('size:'):
                prefs['size'] = c.split(':', 1)[1]

        return prefs
