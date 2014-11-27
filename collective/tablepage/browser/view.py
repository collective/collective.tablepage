# -*- coding: utf-8 -*-

import uuid
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five.browser import BrowserView
from collective.tablepage import config
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import IFieldValidator
from persistent.dict import PersistentDict
from plone.memoize.view import memoize
from zope.component import getAdapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface
from zope.interface import implements

try:
    from Products.CMFEditions.utilities import isObjectChanged
    from Products.CMFEditions.utilities import maybeSaveVersion
    from Products.CMFEditions.utilities import isObjectVersioned
    VERSIONING_SUPPORT = True
except ImportError:
    # No versioning support for Plone 3.3 version of CMFEditions
    VERSIONING_SUPPORT = False


class ITableEditView(Interface):
    """Marker interface for TableEditView"""


class TableEditView(BrowserView):
    """Render the table for editing it"""
    implements(ITableEditView)

    def __call__(self, *args, **kwargs):
        """If view is called without b_start params, redirect me to last page"""
        request = self.request
        context = self.context
        if 'b_start' not in request.form.keys() and context.getInsertType()=='append':
            batch = self.table_view.batch()
            if batch.lastpage - 1 > 0:
                request.response.redirect("%s/edit-table?b_start:int=%d" % (context.absolute_url(),
                                                                            batch.pagesize * (batch.lastpage - 1)))
                return
        return self.index()

    @property
    @memoize
    def table_view(self):
        table_view = getMultiAdapter((self.context, self.request), name=u'view-table')
        table_view.edit_mode = True
        return table_view

    @memoize
    def portal_url(self):
        return getMultiAdapter((self.context, self.request),
                               name=u'plone_portal_state').portal_url()

    def render_table(self):
        return self.table_view()


class EditRecordView(BrowserView):
    """View for display the edit form for a row"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.set('disable_border', True)
        self.configuration = self.context.getPageColumns()
        self.row_index = None
        self.data = {}
        self.errors = {}

    def __call__(self, *args, **kwargs):
        context = self.context
        request = self.request
        form = request.form
        self.row_index = form.get('row-index', None)
        b_start = form.get('b_start', None)
        if form.get('cancel'):
            request.response.redirect("%s/edit-table%s" % (context.absolute_url(),
                                                           b_start and '?b_start:int=%d' % b_start or ''))
            return
        if form.get('form.submitted'):
            # saving
            putils = getToolByName(context, 'plone_utils')
            self._save()
            if self.errors:
                del form['form.submitted']
                self.data.update(**form)
                return self.index()
            putils.addPortalMessage(_('Row has been saved'))
            request.response.redirect("%s/edit-table%s" % (context.absolute_url(),
                                                           b_start and '?b_start:int=%d' % b_start or ''))
            return
        elif self.row_index is not None and not form.get('addRow'):
            # load an existing row
            if not self.check_manager_or_mine_record(self.row_index):
                raise Unauthorized("You can't modify that record")
            else:
                self.data = self.storage[self.row_index]
        return self.index()

    def _last_index_in_section(self, row_index):
        """Find the last row in that section"""
        storage = self.storage
        storage_size = len(storage)
        if row_index==-1:
            return storage_size
        for x in range(row_index, storage_size):
            if storage[x].get('__label__') and x==row_index:
                # the label is also the last element in the section
                return x+1
            if storage[x].get('__label__'):
                return x
        return storage_size

    def _first_index_in_section(self, row_index):
        """Find the first row in that section"""
        storage = self.storage
        if row_index<=0:
            return storage[0].get('__label__') and 1 or 0
        for x in range(row_index, 0, -1):
            if storage[x].get('__label__') and x==row_index:
                # the label is also the first element in the section
                return x+1
            if storage[x].get('__label__'):
                return x+1
        return 0

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
        """Save a new row or update one"""
        form = self.request.form
        context = self.context
        storage = self.storage
        configuration = self.configuration
        row_index = form.get('row-index', -1)
        tp_catalog = getToolByName(context, config.CATALOG_ID)
        if context.getInsertType()=='prepend':
            # this is the first row in the section, so you want to add something above it
            row_index = self._first_index_in_section(row_index)
        else:
            # this is the last row in the section, so you want to add something below it (default)
            row_index = self._last_index_in_section(row_index)
        # Run validations
        for conf in configuration:
            id = conf['id']
            col_type = conf['type']
            field = getMultiAdapter((context, self.request),
                                    IColumnField, name=col_type)

            validators = getAdapters((field, ),
                                     IFieldValidator)
            for name, validator in validators:
                msg = validator.validate(conf)
                if msg:
                    self.errors[id] = msg
                    break

        to_be_saved = {}
        if not self.errors:
            # As some IColumnDataRetriever adapter do some stuff, we read data only if no error has been get
            for conf in configuration:
                id = conf['id']
                col_type = conf['type']
                try:
                    retriever = getAdapter(context,
                                           IColumnDataRetriever,
                                           name=col_type)
                except ComponentLookupError:
                    retriever = IColumnDataRetriever(context)
                try:
                    data = retriever.get_from_request(id, form)
                except NotImplementedError:
                    data = None
                if data:
                    to_be_saved.update(**data)
        else:
            putils = getToolByName(context, 'plone_utils')
            putils.addPortalMessage(pmf(u'Please correct the indicated errors.'), type="error")
            return
        
        if to_be_saved:
            member = getMultiAdapter((context, self.request), name=u'plone_portal_state').member()
            _ = getToolByName(context, 'translation_service').utranslate
            if form.get('row-index') is not None and not form.get('addRow'):
                # Edit row
                row_index = form.get('row-index')
                if not self.check_manager_or_mine_record(row_index):
                    raise Unauthorized("You can't modify that record")
                to_be_saved['__uuid__'] = storage[row_index]['__uuid__']
                storage.update(row_index, to_be_saved)
                self._addNewVersion(_(msgid="Row changed",
                                      domain="collective.tablepage",
                                      context=context))
            else:
                # Add row
                to_be_saved['__creator__'] = member.getId()
                to_be_saved['__uuid__'] = str(uuid.uuid4())
                storage.add(to_be_saved, row_index)
                self._addNewVersion(_(msgid="Row added",
                                      domain="collective.tablepage",
                                      context=context))
            self._populateCache(storage, row_index)
            tp_catalog.catalog_row(context, storage[row_index])

    def _populateCache(self, storage, index):
        """Pre-populate cache with data in the storage"""
        # Commonly called before first read attempt
        context = self.context
        record = storage[index]
        adapters = {}
        now = DateTime().millis()
        if record.get("__cache__") is None:
            record["__cache__"] = PersistentDict()
        for conf in context.getPageColumns():
            id = conf['id']
            col_type = conf['type']
            if not adapters.get(col_type):
                adapters[col_type] = getMultiAdapter((context, self.request),
                                                     IColumnField, name=col_type)
            field = adapters[conf['type']]
            field.configuration = conf
            if not field.cache_time:
                continue
            output = field.render_view(record.get(id), index)
            record["__cache__"][id] = PersistentDict()
            record["__cache__"][id]['data'] = output
            record["__cache__"][id]['timestamp'] = now

    def _addNewVersion(self, comment=''):
        """Content must be updated, so the history machinery will save a new version"""
        context = self.context
        context.reindexObject()
        if VERSIONING_SUPPORT and isObjectChanged(context) and isObjectVersioned(context):
            maybeSaveVersion(context, comment=comment)


class DeleteRecordView(EditRecordView):
    """Delete rows from the table"""
    
    def __call__(self):
        context = self.context
        request = self.request
        indexes = self.request.form.get('row-index')
        b_start = request.form.get('b_start', None)
        tp_catalog = getToolByName(context, config.CATALOG_ID)

        if indexes is not None:
            member = getMultiAdapter((context, request), name=u'plone_portal_state').member()
            putils = getToolByName(context, 'plone_utils')
            _ = getToolByName(context, 'translation_service').utranslate
            sm = getSecurityManager()
            # check permissions: must be the owner user or have the "Manage table" permission
            storage = self.storage
            if isinstance(indexes, int):
                # we get an int when clicking on single row delete command
                indexes = [indexes,]
            for c, index in enumerate(indexes):
                if not sm.checkPermission(config.MANAGE_TABLE, context) \
                            and member.getId()!=storage[index-c].get('__creator__'):
                        raise Unauthorized("You can't delete that record")
                tp_catalog.uncatalog_row(context, storage[index-c].get('__uuid__'))
                del storage[index-c]

            # Now we need to reindex all rows that follow, to fill the hole
            min_index = min(indexes)
            self._reindex_following(min_index-c)

            if len(indexes)==1:
                msg = _(msgid="Row deleted",
                        domain="collective.tablepage",
                        context=context)
            else:
                msg = _(msgid='${count} rows deleted',
                        domain="collective.tablepage",
                        mapping={'count': len(indexes)},
                        context=context)
            putils.addPortalMessage(msg)
            # if the table is changed, the content is changed 
            self._addNewVersion(msg)

        request.response.redirect("%s/edit-table%s" % (context.absolute_url(),
                                                       b_start and '?b_start:int=%d' % b_start or ''))

    def _reindex_following(self, start_from):
        context = self.context
        storage = self.storage
        tp_catalog = getToolByName(context, config.CATALOG_ID)
        for row in storage[start_from:]:
            tp_catalog.catalog_row(context, row, idxs=['getObjPositionInParent'])


class MoveRecordView(EditRecordView):
    """Move a row on the table"""

    def __call__(self):
        form = self.request.form
        context = self.context
        index = form.get('row-index')
        direction = form.get('direction')
        b_start = form.get('b_start', None)

        if index is not None and direction in ('up', 'down'):
            tp_catalog = getToolByName(context, config.CATALOG_ID)
            direction = direction=='up' and -1 or 1
            storage = self.storage
            row = storage[index]
            del storage[index]
            storage.add(row, index+direction)
            tp_catalog.reindex_rows(context, [row['__uuid__'], storage[index]['__uuid__']])
            putils = getToolByName(context, 'plone_utils')
            _ = getToolByName(context, 'translation_service').utranslate
            putils.addPortalMessage(_(msgid='Row has been moved',
                                      domain="collective.tablepage",
                                      context=context))
            # if the table is changed, the content is changed
            self._addNewVersion(_(msgid="Row moved",
                                  domain="collective.tablepage",
                                  context=context))
        self.request.response.redirect("%s/edit-table%s" % (context.absolute_url(),
                                                            b_start and '?b_start:int=%d' % b_start or ''))
