# -*- coding: utf-8 -*-

import transaction
from Acquisition import aq_inner
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from collective.tablepage import logger
from collective.tablepage import config
from collective.tablepage import tablepageMessageFactory
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IDataStorage
from persistent.dict import PersistentDict
from plone.memoize.view import memoize
from zope.component import getMultiAdapter

try:
    from plone.batching import Batch
except ImportError:
    from Products.CMFPlone.PloneBatch import Batch


class TableViewView(BrowserView):
    """Render only the table"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.datagrid = context.getField('pageColumns')
        self.edit_mode = False
        self.last_page_label = {}
        self.b_start = 0
        self.result_length = 0
        self.now = DateTime()
        self._rows = []

    def __call__(self):
        storage = self.storage
        if not self.edit_mode and len(storage)==0:
            return ""
        if self.edit_mode:
            return self.index()
        return self._transformed(self.index())

    def _transformed(self, data, mt='text/x-html-safe'):
        """
        Use the safe_html transform to protect text output. This also
        ensures that resolve UID links are transformed into real links.
        """
        orig = data
        context = aq_inner(self.context)

        if not isinstance(orig, unicode):
            # Apply a potentially lossy transformation, and hope we stored
            # utf-8 text. There were bugs in earlier versions of this portlet
            # which stored text directly as sent by the browser, which could
            # be any encoding in the world.
            orig = unicode(orig, 'utf-8', 'ignore')
            logger.warn("Table at %s has stored non-unicode text. "
                "Assuming utf-8 encoding." % context.absolute_url())

        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo(mt, orig,
                                     context=context, mimetype='text/html')
        result = data.getData()
        if result:
            if isinstance(result, str):
                return unicode(result, 'utf-8')
            return result
        return ''

    @property
    @memoize
    def storage(self):
        return IDataStorage(self.context)

    @property
    def is_empty(self):
        return self.result_length==0

    def showHeaders(self):
        """Logic for display table headers"""
        show_headers_options = self.context.getShowHeaders()
        if show_headers_options and show_headers_options!='always':
            if show_headers_options=='view_only' and self.edit_mode:
                return False
            if show_headers_options=='edit_only' and not self.edit_mode:
                return False
        return True

    def headers(self):
        data = self.datagrid.get(self.context)
        results = []
        for d in data:
            if not d:
                continue
            results.append(dict(label=tablepageMessageFactory(d['label'].decode('utf-8')),
                                description=tablepageMessageFactory(d.get('description', '').decode('utf-8')),
                                classes='coltype-%s' % d['type'],
                                ))
        return results

    def _findLastPageLabel(self, b_start):
        """
        Given an index to start, find the first previous label in the same table.
        Used. to replicate the label on new pages on batching
        """
        storage = self.storage
        for index in range(b_start, 0, -1):
            if self.is_label(index):
                return storage[index]['__label__']
        return {}

    def _clean_query(self, d):
        """Return a copy of the dict where empty values are omitted"""
        return dict((k, v) for k, v in d.iteritems() if v)

    def rows(self, batch=False, bsize=0, b_start=0, search=False, ignore_cache=False):
        context = self.context
        request = self.request
        if not search:
            storage = self.storage
            self.result_length = len(storage)
        else:
            tp_catalog = getToolByName(context, 'tablepage_catalog')
            storage = tp_catalog.searchTablePage(context, **self._clean_query(request.form))
            self.result_length = getattr(storage, 'actual_result_count') or len(storage)

        rows = []
        adapters = {}
        # check if b_start is out on index
        if b_start>self.result_length:
            b_start = 0
        b_start

        # let's cache adapters
        for conf in self.context.getPageColumns():
            col_type = conf['type']
            adapters[col_type] = getMultiAdapter((context, request),
                                                 IColumnField, name=col_type)

        self.last_page_label = self._findLastPageLabel(b_start)

        index = b_start
        write_attempt_count = 0
        for record in storage[b_start:bsize and (b_start+bsize) or None]:
            if search:
                record = self.storage[record.UID]
            if batch and index >= b_start+bsize:
                # Ok, in this way we display always bsize rows, not bsize rows of data
                # But is enough for now
                # BBB: can this be true ever?
                break
            
            if record.get('__label__') or getattr(record, 'is_label', False):
                rows.append(record.get('__label__') or getattr(record, 'label'))
                index += 1
                continue

            row = []
            write_attempt = False
            for conf in context.getPageColumns():
                field = adapters[conf['type']]
                field.configuration = conf
                # Cache hit
                if not ignore_cache and field.cache_time and record.get("__cache__", {}).get(conf['id']) and \
                        self.now.millis() < record["__cache__"][conf['id']]['timestamp'] + field.cache_time * 1000:
                    output = record["__cache__"][conf['id']]['data']
                    logger.debug("Cache hit (%s)" % conf['id'])
                # Cache miss
                else:
                    output = field.render_view(record.get(conf['id']), index)
                    if field.cache_time:
                        if not record.get("__cache__"):
                            record["__cache__"] = PersistentDict()
                        record["__cache__"][conf['id']] = PersistentDict()
                        record["__cache__"][conf['id']]['data'] = output
                        record["__cache__"][conf['id']]['timestamp'] = self.now.millis()
                        write_attempt = True
                        logger.debug("Cache miss (%s)" % conf['id'])
                row.append({'content': output,
                            'classes': 'coltype-%s' % col_type})
            rows.append(row)
            index += 1
            if write_attempt:
                write_attempt_count += 1
            if write_attempt_count and write_attempt_count % 100 == 0:
                transaction.savepoint()
                logger.info('Writing to cache fresh data (%d rows done)' % write_attempt_count)
        return rows

    def batch(self, batch=True, bsize=0, b_start=0):
        request = self.request
        self.b_start = b_start or request.form.get('b_start') or 0
        perform_search = 'searchInTable' in request.form.keys()

        bsize = bsize or self.context.getBatchSize() or request.form.get('bsize') or 0
        batch = batch and bsize>0 

        if not batch:
            self._rows = self.rows(search=perform_search)
            return self._rows

        self._rows = self.rows(batch=batch, bsize=bsize, b_start=self.b_start, search=perform_search)        
        # replicating foo elements to reach total size
        self._rows = [None] * self.b_start + self._rows + [None] * (self.result_length - self.b_start - bsize)
        return Batch(self._rows, bsize, start=self.b_start, end=self.b_start+bsize,
                     orphan=int(bsize/10), overlap=0, pagerange=7)

    def batching_enabled(self):
        return self.context.getBatchSize() > 0 

    @memoize
    def portal_url(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state').portal_url()

    @property
    @memoize
    def member(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state').member()

    def check_tablemanager_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission(config.MANAGE_TABLE, self.context)

    def check_labeling_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission(config.MANAGE_LABEL, self.context)

    def check_manage_search_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission(config.MANAGE_SEARCH_PERMISSION, self.context)        

    def mine_row(self, index):
        storage = self.storage
        return storage[index].get('__creator__')==self.member.getId()

    def is_label(self, index):
        if self._rows:
            return  isinstance(self._rows[index], basestring)
        storage = self.storage
        return '__label__' in  storage[index].keys()

    def next_is_label(self, row_index):
        """True if next row is a label (or end of rows)""" 
        if self._rows:
            storage = self._rows
        else:
            storage = self.storage
        storage_size = len(storage)
        next_index = row_index + 1
        return next_index>=storage_size or self.is_label(next_index)

    def css_classes(self):
        table_classes = ['tablePage',  'nosort' ]
        table_classes.extend(self.context.getCssClasses())
        if self.edit_mode:
            table_classes.append('editing')
        return ' '.join(table_classes)

    def template_id(self):
        # Used due to bugged Plone 3.3 integration with batch
        # On Plone 4.3/plone.batching is ok
        if self.edit_mode:
            return 'edit-table'
        return ''

