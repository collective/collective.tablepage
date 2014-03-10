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


class TableViewView(BrowserView):
    """Render only the table"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.datagrid = context.getField('pageColumns')
        self.edit_mode = False

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

    def rows(self):
        storage = self.storage
        rows = []
        adapters = {}
        
        # let's cache adapters
        for conf in self.context.getPageColumns():
            col_type = conf['type']
            adapters[col_type] = getMultiAdapter((self.context, self.request),
                                                 IColumnField, name=col_type)
            adapters[col_type].configuration = conf

        for index, record in enumerate(storage):
            if record.get('__label__'):
                rows.append(record.get('__label__'))
                continue
            row = []
            for conf in self.context.getPageColumns():
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
        return rows

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
        