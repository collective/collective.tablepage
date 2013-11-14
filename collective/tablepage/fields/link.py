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
    from plone.uuid.interfaces import IUUID
except ImportError:
    IUUID = None

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

def get_uuid(obj):
    # BBB: can be removed when we get rid of Plone 3.3 compatibility
    if IUUID is not None:
        return IUUID(obj)
    return obj.UID() # AT only


class LinkedObjectFinder(object):
    """Service class with some methods useful for getting referenced objects"""

    def get_referenced_object_from_path(self, path):
        """If you call on /folder/content1 you'll get uuid of content1 inside the folder"""
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        portal = portal_state.portal()
        if path.startswith('/'):
            path = path[1:]
        obj = portal.restrictedTraverse(path, None)
        if obj and path:
            return get_uuid(obj)

    def get_referenced_object_from_URL(self, URL):
        """If you call on http://myhost/plone/content1 you'll get uuid of content1"""
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        if URL.startswith(portal_state.portal_url()):
            path = URL.replace(portal_state.portal_url(), '')
            return self.get_referenced_object_from_path(path)


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
        return self.view_template(data=self.data)

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
            return obj and {'title': obj.Title().decode('utf-8'), 'uuid':  obj.UID()} or None


class LinkDataRetriever(LinkedObjectFinder):
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

    def data_for_display(self, data, backend=False):
        """Get proper URL to the resource mapped by an uuid, or directly the URL"""
        if data:
            if is_url(data):
                return data
            uuid = data
            rcatalog = getToolByName(self.context, 'reference_catalog')
            obj = rcatalog.lookupObject(uuid)
            if obj:
                return backend and get_uuid(obj) or obj.absolute_url()
        return ''

    def data_to_storage(self, data):
        """Check if data is a valid uuid or an URL/path to a content"""
        if data:
            url_format = is_url(data)
            if not url_format:
                uuid = self.data_for_display(data, backend=True) or None
                if uuid:
                    return uuid
            portal_state = getMultiAdapter((self.context, self.context.REQUEST),
                                           name=u'plone_portal_state')
            portal_url = portal_state.portal_url()
            if data.startswith(portal_url):
                return self.get_referenced_object_from_URL(data)
            if not url_format:
                # fallback: let try if this is a path
                return self.get_referenced_object_from_path(data)
            return data
