# -*- coding: utf-8 -*-

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
            logger.warn("Static portlet at %s has stored non-unicode text. "
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

    def rows(self, batch=False, bsize=0, b_start=0):
        storage = self.storage
        context = self.context
        request = self.request

        rows = []
        adapters = {}
        # check if b_start is out on index
        if b_start>len(storage):
            b_start = 0
        b_start

        # let's cache adapters
        for conf in self.context.getPageColumns():
            col_type = conf['type']
            adapters[col_type] = getMultiAdapter((context, request),
                                                 IColumnField, name=col_type)
            adapters[col_type].configuration = conf

        self.last_page_label = self._findLastPageLabel(b_start)

        index = b_start
        for record in storage[b_start:]:

            if batch and index >= b_start+bsize:
                # Ok, in this way we display always bsize rows, not bsize rows of data
                # But is enough for now
                break
            
            if record.get('__label__'):
                rows.append(record.get('__label__'))
                index += 1
                continue

            row = []
            for conf in context.getPageColumns():
                field = adapters[conf['type']]
                now = DateTime()
                # Cache hit
                if field.cache_time and record.get("__cache__", {}).get(conf['id']) and \
                        now.millis() < record["__cache__"][conf['id']]['timestamp'] + field.cache_time * 1000:
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
                        record["__cache__"][conf['id']]['timestamp'] = now.millis()
                        logger.debug("Cache miss (%s)" % conf['id'])
                row.append({'content': output,
                            'classes': 'coltype-%s' % col_type})
            rows.append(row)
            index += 1
        return rows

    def batch(self, batch=True, bsize=0, b_start=0):
        request = self.request
        storage_size = len(self.storage)
        self.b_start = b_start or request.form.get('b_start') or 0
        # check if b_start_ make sense
        if self.b_start > storage_size:
            self.b_start = 0
        bsize = bsize or self.context.getBatchSize() or request.form.get('bsize') or 0
        batch = batch and bsize>0 

        if not batch:
            return self.rows()

        rows = self.rows(batch, bsize, self.b_start)        
        # replicating foo elements to reach total size
        rows = [None] * self.b_start + rows + [None] * (storage_size - self.b_start - bsize)
        return Batch(rows, bsize, start=self.b_start, end=self.b_start+bsize,
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

    def mine_row(self, index):
        storage = self.storage
        return storage[index].get('__creator__')==self.member.getId()

    def is_label(self, index):
        storage = self.storage
        return '__label__' in  storage[index].keys()

    def next_is_label(self, row_index):
        """True if next row is a label (or end of rows)""" 
        storage = self.storage
        storage_size = len(storage)
        next_index = row_index + 1
        if next_index>=storage_size:
            return True
        if self.is_label(next_index):
            return True
        return False

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

