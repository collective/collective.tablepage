# -*- coding: utf-8 -*-

# A LOT of mess can be removed from this field as soon as we will drop Plone 3.3 compatibility
# I hope to live long enough to see that day

import sys
from Products.CMFCore.utils import getToolByName
from collective.tablepage.fields.base import BaseField
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.interfaces import IColumnField
from zope.component import getMultiAdapter
from zope.interface import implements

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


if sys.version_info < (2, 6):
    PLONE3 = True
else:
    PLONE3 = False


def is_url(data):
    data = data.lower()
    return data.startswith('http://') or data.startswith('/') or data.startswith('../') \
            or data.startswith('https://') or data.startswith('ftp://')


class LinkField(BaseField):
    implements(IColumnField)

    def __init__(self, context, request):
        BaseField.__init__(self, context, request)
        self.PLONE3 = PLONE3

    edit_template = ViewPageTemplateFile('templates/link.pt')
    view_template = ViewPageTemplateFile('templates/link_view.pt')

    def portal_url(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()

    def getStartupDirectory(self):
        """Startup directory in pure atreferencebrowser widget style"""
        storage = self.context.getAttachmentStorage() or self.context
        return storage.absolute_url()

    def render_view(self, data):
        self.data = data or ''
        if self.data:
            if is_url(self.data):
                return self.view_template(external_url=self.data)
            # probably an uid
            uuid = self.data
            obj_info = self._get_obj_info(uuid)
            return self.view_template(**obj_info)
        return self.view_template(data=uuid)

    def render_edit(self, data):
        data = data or ''
        self.data = data.decode('utf-8')
        if not is_url(self.data):
            return self.edit_template(data=self.data)
        return self.edit_template(external_url=self.data)

    def getReferencedDocument(self):
        uuid = self.data
        if uuid:
            rcatalog = getToolByName(self.context, 'reference_catalog')
            obj = rcatalog.lookupObject(uuid)
            return obj


class LinkDataRetriever(object):
    """Get data from the request, that can be a uid to an element"""

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        # internal link take precedence
        if request.get("internal_%s" % name):
            return {name: request.get("internal_%s" % name)}
        if request.get("external_%s" % name, '').strip():
            return {name: request.get("external_%s" % name)}
        return None

    def data_for_display(self, data):
        """Get proper URL to the resource mapped by an uuid, or directly the URL"""
        if data:
            if is_url(data):
                return data
            uuid = data
            rcatalog = getToolByName(self.context, 'reference_catalog')
            obj = rcatalog.lookupObject(uuid)
            if obj:
                return obj.absolute_url()
        return ''
