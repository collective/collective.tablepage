# -*- coding: utf-8 -*-

from Acquisition import aq_inner, aq_parent
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.link import LinkedObjectFinder
from plone.memoize.instance import memoize
from AccessControl import Unauthorized

from Products.ATContentTypes.permission import permissions

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

TYPE_TO_CREATE = 'File'


class FileField(BaseField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/file.pt')
    view_template = ViewPageTemplateFile('templates/file_view.pt')

    def render_view(self, data):
        self.data = data or ''
        uuid = data
        obj_info = self._get_obj_info(uuid)
        if obj_info:
            return self.view_template(**obj_info)
        return ''

    def can_add_file(self):
        member = getMultiAdapter((self.context, self.request), name=u'plone_portal_state').member()
        return member.has_permission(permissions[TYPE_TO_CREATE], self.attachment_storage)

    @property
    @memoize
    def attachment_storage(self):
        try:
            attachment_storage = self.context.getAttachmentStorage() or aq_parent(aq_inner(self.context))
            # just check permissions
            self.context.restrictedTraverse('/'.join(attachment_storage.getPhysicalPath()))
            return attachment_storage
        except Unauthorized:
            return None

    def attachments(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        files_in_storage = catalog(portal_type='File',
                                   path={'query': '/'.join(self.attachment_storage.getPhysicalPath()),
                                         'depth': 1,
                                         },
                                   order_by = 'getObjPositionInParent')
        if self.data:
            # we must handle the special case where the storage has been changed and
            # when editing we haven't the old file still there
            old = catalog(UID=self.data)
            if old and old[0].getPath() not in [a.getPath() for a in files_in_storage]:
                return old + files_in_storage 
        return files_in_storage


class MultipleFilesField(FileField):
    implements(IColumnField)

    edit_template = ViewPageTemplateFile('templates/multi_file.pt')
    view_template = ViewPageTemplateFile('templates/multi_file_view.pt')

    def render_edit(self, data):
        self.data = data and data.splitlines() or []
        return self.edit_template(data=self.data)

    def render_view(self, data):
        self.data = data or ''
        results = []
        for uuid in self.data.splitlines():
            obj_info = self._get_obj_info(uuid)
            if obj_info:
                results.append(obj_info)
        if results:
            return self.view_template(files=results)
        return ''

    def attachments(self, filterUIDs=[]):
        if filterUIDs is None:
            return []
        if not filterUIDs:
            return FileField.attachments(self)
        catalog = getToolByName(self.context, 'portal_catalog')
        files_in_storage = []
        for uid in filterUIDs:
            file_in_storage = catalog(portal_type='File',
                                      path={'query': '/'.join(self.attachment_storage.getPhysicalPath()),
                                            'depth': 1,
                                            },
                                      UID = uid,
                                      order_by = 'getObjPositionInParent')
            if file_in_storage:
                files_in_storage.append(file_in_storage[0])
        return files_in_storage


class FileDataRetriever(LinkedObjectFinder):
    """
    The implementation of IColumnDataRetriever for file will:
     * save a new File content type in the folder
     * return the UID of the new File
    """

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        if request.get(name) and request.get(name).filename:
            folder = self.context.getAttachmentStorage() or aq_parent(aq_inner(self.context))
            title = request.get('title_%s' % name)
            description = request.get('description_%s' % name)
            file = request.get(name)
            newId = folder.generateUniqueId(TYPE_TO_CREATE)
            if not title and file.filename in folder.objectIds():
                # WARNING: we don't get the file title, to obtain the id
                plone_utils = getToolByName(self.context, 'plone_utils')
                plone_utils.addPortalMessage(_('duplicate_file_error',
                                               default=u'There is already an item named ${name} in this folder.\n'
                                                       u'Loading of the attachment has been aborted.',
                                               mapping={'name': file.filename}),
                                             type='warning')
                return {name: folder[file.filename].UID()}
            folder.invokeFactory(id=newId, type_name=TYPE_TO_CREATE,
                                 title=title, description=description)
            new_doc = folder[newId]
            # force rename (processForm will not work with files)
            new_doc._renameAfterCreation()
            # this will trigger proper lifecycle events
            new_doc.processForm()
            new_doc.edit(file=file)
            return {name: new_doc.UID()}
        elif request.get("existing_%s" % name):
            return {name: request.get("existing_%s" % name)}
        return None

    def data_for_display(self, data, backend=False):
        """Get proper URL to the resource mapped by an uuid"""
        uuid = data
        rcatalog = getToolByName(self.context, 'reference_catalog')
        obj = rcatalog.lookupObject(uuid)
        if obj:
            return backend and obj.UID() or obj.absolute_url()
        return ''

    def data_to_storage(self, data):
        """Check if data is a valid uuid or an URL/path to a content"""
        if data:
            uuid = self.data_for_display(data, backend=True) or None
            if uuid:
                return uuid
            portal_state = getMultiAdapter((self.context, self.context.REQUEST),
                                           name=u'plone_portal_state')
            portal_url = portal_state.portal_url()
            if data.startswith(portal_url):
                return self.get_referenced_object_from_URL(data)
            # fallback: let try if this is a path
            return self.get_referenced_object_from_path(data)


class MultipleFilesDataRetriever(LinkedObjectFinder):
    """
    The implementation of IColumnDataRetriever for multiple files will:
     * save a set of Files content type in the folder
     * return a list of UID
    """

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        results = []
        context = self.context
        folder = context.getAttachmentStorage() or aq_parent(aq_inner(context))
        plone_utils = getToolByName(context, 'plone_utils')
        # first of all we need also to check for existings selected files
        for existing_selection in request.get("existing_%s" % name, []):
            results.append(existing_selection)
        cnt = 0
        while True:
            if request.get("%s_%s" % (name, cnt)) and request.get("%s_%s" % (name, cnt)).filename:
                title = request.get('title_%s_%s' % (name, cnt))
                description = request.get('description_%s_%s' % (name, cnt))
                file = request.get("%s_%s" % (name, cnt))
                cnt += 1
                newId = folder.generateUniqueId(TYPE_TO_CREATE)
                if not title and file.filename in folder.objectIds():
                    # WARNING: we don't get the file title, to obtain the id
                    plone_utils.addPortalMessage(_('duplicate_file_error',
                                                   default=u'There is already an item named ${name} in this folder.\n'
                                                           u'Loading of the attachment has been aborted.',
                                                   mapping={'name': file.filename}),
                                                 type='warning')
                    results.append(folder[file.filename].UID())
                    continue
                folder.invokeFactory(id=newId, type_name=TYPE_TO_CREATE,
                                     title=title, description=description)
                new_doc = folder[newId]
                # force rename (processForm will not work with files)
                new_doc._renameAfterCreation()
                # this will trigger proper lifecycle events
                new_doc.processForm()
                new_doc.edit(file=file)
                results.append(new_doc.UID())
            else:
                break
        return {name: '\n'.join(results)}

    def data_for_display(self, data, backend=False):
        """Get proper URL to the resource mapped by an uuid"""
        rcatalog = getToolByName(self.context, 'reference_catalog')
        results = []
        for uuid in data.splitlines():
            obj = rcatalog.lookupObject(uuid)
            if obj:
                results.append(backend and obj.UID() or obj.absolute_url())
        return results

    def data_to_storage(self, data):
        """Check if data is a set of valid uuids or URL/path to a contents"""
        if not data:
            return None
        results = []
        portal_state = getMultiAdapter((self.context, self.context.REQUEST),
                                       name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        for entry in data.splitlines():
            uuid = self.data_for_display(entry, backend=True) or None
            if uuid:
                results.append(uuid[0])
                continue
            if entry.startswith(portal_url):
                uuid = self.get_referenced_object_from_URL(entry)
                if uuid:
                    results.append(uuid)
                    continue
            # fallback: let try if this is a path
            uuid = self.get_referenced_object_from_path(entry)
            if uuid:
                results.append(uuid)
        if results:
            return '\n'.join(results)
