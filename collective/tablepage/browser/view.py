# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from collective.tablepage import config
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage import tablepageMessageFactory as _
from AccessControl import getSecurityManager

try:
    from Products.CMFEditions.utilities import isObjectChanged
    from Products.CMFEditions.utilities import maybeSaveVersion
    from Products.CMFEditions.utilities import isObjectVersioned
    VERSIONING_SUPPORT = True
except ImportError:
    # No versioning support for Plone 3.3 version of CMFEditions
    VERSIONING_SUPPORT = False


class TableEditView(BrowserView):
    """Render the table for editing it"""

    @memoize
    def portal_url(self):
        return getMultiAdapter((self.context, self.request),
                               name=u'plone_portal_state').portal_url()

    def render_table(self):
        table_view = getMultiAdapter((self.context, self.request), name=u'view-table')
        table_view.edit_mode = True
        return table_view()


class EditRecordView(BrowserView):
    """View for display the edit form for a row"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.set('disable_border', True)
        self.configuration = self.context.getPageColumns()
        self.data = {}

    def __call__(self, *args, **kwargs):
        request = self.request
        form = request.form
        if form.get('cancel'):
            request.response.redirect("%s/edit-table" % self.context.absolute_url())
            return
        if form.get('form.submitted'):
            # saving
            putils = getToolByName(self.context, 'plone_utils')
            self._save()
            putils.addPortalMessage(_('Row has been saved'))
            request.response.redirect("%s/edit-table" % self.context.absolute_url())
            return
        elif form.get('row-index') is not None:
            # load an existing row
            if not self.check_manager_or_mine_record(form.get('row-index')):
                raise Unauthorized("You can't modify that record")
            self.data = self.storage[form.get('row-index')]
        return self.index()

    def fields(self):
        """Display all fields for this content"""
        fields = []
        for conf in self.configuration:
            col_type = conf['type']
            field = getMultiAdapter((self.context, self.request),
                                    IColumnField, name=col_type)
            field.configuration = conf
            fields.append(field)
        return fields

    @property
    @memoize
    def storage(self):
        return IDataStorage(self.context)

    def check_manager_or_mine_record(self, index):
        """Security check on a record in the storage"""
        storage = self.storage
        context = self.context
        member = getMultiAdapter((context, self.request), name=u'plone_portal_state').member()
        sm = getSecurityManager()
        # check permissions: must be the owner user or have the "Manage table" permission
        if not sm.checkPermission(config.MANAGE_TABLE, context) \
                    and member.getId()!=storage[index].get('__creator__'):
            return False
        return True

    def _save(self):
        form = self.request.form
        context = self.context
        storage = self.storage
        configuration = self.configuration

        to_be_saved = {}
        for conf in configuration:
            id = conf['id']
            col_type = conf['type']
            try:
                retriever = getAdapter(context,
                                       IColumnDataRetriever,
                                       name=col_type)
            except ComponentLookupError:
                retriever = IColumnDataRetriever(context)
            data = retriever.get_from_request(id, form)
            if data:
                to_be_saved.update(**data)
        if to_be_saved:
            member = getMultiAdapter((context, self.request), name=u'plone_portal_state').member()
            if form.get('row-index') is not None:
                index = form.get('row-index')
                if not self.check_manager_or_mine_record(index):
                    raise Unauthorized("You can't modify that record")
                storage.update(index, to_be_saved)
            else:
                to_be_saved['__creator__'] = member.getId()
                storage.add(to_be_saved)
            # if the table is changed, the content is changed
            _ = getToolByName(context, 'translation_service').utranslate
            self._addNewVersion(_(msgid="Row changed",
                                  domain="collective.tablepage",
                                  context=context))

    def _addNewVersion(self, comment=''):
        """Content must be updated, so the history machinery will save a new version"""
        context = self.context
        context.reindexObject()
        if VERSIONING_SUPPORT and isObjectChanged(context) and isObjectVersioned(context):
            maybeSaveVersion(context, comment=comment)


class DeleteRecordView(EditRecordView):
    """Delete a row on the table"""
    
    def __call__(self):
        context = self.context
        index = self.request.form.get('row-index')
        if index is not None:
            member = getMultiAdapter((context, self.request), name=u'plone_portal_state').member()
            sm = getSecurityManager()
            # check permissions: must be the owner user or have the "Manage table" permission
            storage = self.storage
            if not sm.checkPermission(config.MANAGE_TABLE, context) \
                        and member.getId()!=storage[index].get('__creator__'):
                    raise Unauthorized("You can't delete that record")
            del storage[index]
            putils = getToolByName(context, 'plone_utils')
            _ = getToolByName(context, 'translation_service').utranslate
            putils.addPortalMessage(_(msgid='Row has been deleted',
                                      domain="collective.tablepage",
                                      context=context))
            # if the table is changed, the content is changed 
            self._addNewVersion(_(msgid="Row deleted",
                                  domain="collective.tablepage",
                                  context=context))
        self.request.response.redirect("%s/edit-table" % context.absolute_url())


class MoveRecordView(EditRecordView):
    """Move a row on the table"""

    def __call__(self):
        index = self.request.form.get('row-index')
        direction = self.request.form.get('direction')
        if index is not None and direction in ('up', 'down'):
            direction = direction=='up' and -1 or 1
            storage = self.storage
            row = storage[index]
            del storage[index]
            storage.add(row, index+direction)
            putils = getToolByName(self.context, 'plone_utils')
            _ = getToolByName(self.context, 'translation_service').utranslate
            putils.addPortalMessage(_(msgid='Row has been moved',
                                      domain="collective.tablepage",
                                      context=self.context))
            # if the table is changed, the content is changed
            self._addNewVersion(_(msgid="Row moved",
                                  domain="collective.tablepage",
                                  context=self.context))
        self.request.response.redirect("%s/edit-table" % self.context.absolute_url())
