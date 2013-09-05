# -*- coding: utf-8 -*-

from Acquisition import aq_inner, aq_parent
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.fields.base import BaseFieldDataRetriever
from collective.tablepage.fields.base import BaseField
from plone.i18n.normalizer.interfaces import IURLNormalizer

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class FileField(BaseField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/file.pt')
    view_template = ViewPageTemplateFile('templates/file_view.pt')

    def render_view(self, data):
        uuid = data
        rcatalog = getToolByName(self.context, 'reference_catalog')
        obj = rcatalog.lookupObject(uuid)
        if obj:
            return self.view_template(title=obj.Title(), url=obj.absolute_url())
        return ''

    def attachment_storage(self):
        attachment_storage = self.context.getAttachmentStorage()
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type='File', path='/'.join(attachment_storage.getPhysicalPath()))


class FileDataRetriever(object):
    """
    The implementation of IColumnDataRetriever for file will:
     * save a new File content type in the folder
     * return the UID of the new File
    """

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        if request.get(name).filename:
            folder = self.context.getAttachmentStorage() or aq_parent(aq_inner(self.context))
            title = request.get('title_%s' % name)
            description = request.get('description_%s' % name)
            file = request.get(name)
            newId = folder.generateUniqueId('File')
            folder.invokeFactory(id=newId, type_name='File', title=title, description=description)
            new_doc = folder[newId]
            new_doc._renameAfterCreation()
            return {name: new_doc.UID()}
        elif request.get("existing_%s" % name):
            return {name: request.get("existing_%s" % name)}
        return None

    def data_for_display(self, data):
        """Get proper URL to the resource mapped by an uuid"""
        uuid = data
        rcatalog = getToolByName(self.context, 'reference_catalog')
        obj = rcatalog.lookupObject(uuid)
        if obj:
            return obj.absolute_url()
        return ''
