# -*- coding: utf-8 -*-

import time
import urllib
from Globals import InitializeClass
from Acquisition import aq_parent, aq_inner
from App.special_dtml import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import search_zcatalog
from AccessControl.Permissions import manage_zcatalog_entries
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from plone.indexer import indexer
from plone.indexer.wrapper import IIndexableObjectWrapper
from plone.indexer.wrapper import IndexableObjectWrapper
from plone.memoize.instance import memoize
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import ITablePage
from collective.tablepage import config
from zope.component import getMultiAdapter
from zope.interface import Interface, implements


class ICatalogDictWrapper(Interface):
    pass

class CatalogDictWrapper(object):
    implements(ICatalogDictWrapper)
    
    def __init__(self, dict_obj, context, path):
        self._path = path
        self._content = context
        self._uuid = path.split('/')[-1][4:]
        for k,v in dict_obj.items():
            if k=='__creator__':
                self.Creator = v
                continue
            elif k=='__uuid__':
                self.UID = v
                continue
            elif k.startswith('_'):
                continue
            if v and v.strip():
                self.__setattr__(k, v.strip())
        self._index_from_cache(dict_obj)

    def _index_from_cache(self, dict_obj):
        # BBB: now, if we use cache, let also index values stored in cache
        # if not already indexed
        # this is tricky, but in this way we can index complex columns
        # like Computed (when cache is used)
        # I know, it's evil and I'm  a bad guy
        if not dict_obj.get('__cache__'):
            return
        for k in dict_obj.get('__cache__').keys():
            if hasattr(self, k):
                # already saved before
                continue
            if k.startswith('_'):
                continue
            # refresh cache before using it.
            # Calling the table page view with ignore_cache will refresh all caches
            table_view = getMultiAdapter((self._content, self._content.REQUEST), name=u'view-table')
            table_view.rows(bsize=1, b_start=self.getObjPositionInParent()-1, ignore_cache=True)
            storage = IDataStorage(self._content)
            v = storage[self.getObjPositionInParent()-1]['__cache__'].get(k)
            if v and v.get('data') and v.get('data').strip():
                self.__setattr__(k, v['data'].strip())

    def getPhysicalPath(self):
        return self._path.split('/')

    @memoize
    def _getRow(self):
        storage = IDataStorage(self._content)
        for index, row in enumerate(storage):
            if row.get('__uuid__')==self._uuid:
                return index, row

    def getObjPositionInParent(self):
        row = self._getRow()
        if row:
            index, data = row
            return index+1
        return 0

    def SearchableText(self):
        """Get searchable text from all column marked as searchable"""
        row = self._getRow()
        if not row:
            return ''
        searchable = ''
        content = self._content
        conf = content.getPageColumns()
        search_conf = content.getSearchConfig()
        index, data = row
        columns = [c['id'] for c in conf]
        for c in [x for x in search_conf if x]: # in this way fix some migration issues
            if c['id'] in columns and 'SearchableText' in c['additionalConfiguration']:
                searchable += data.get(c['id'], '') + ' '
        return searchable


@indexer(ICatalogDictWrapper)
def getObjPositionInParent(obj):
    return obj.getObjPositionInParent()


class TablePageCatalog(CatalogTool):
    """Rows catalog for Table page"""

    id = config.CATALOG_ID
    title = "TablePage Catalog"

    security = ClassSecurityInfo()

    manage_catalogAdvanced = DTMLFile('www/catalogAdvanced', globals())

    def __init__(self):
        ZCatalog.__init__(self, self.getId(), self.title)

    security.declareProtected(search_zcatalog, 'searchTablePage')
    def searchTablePage(self, tp, **kwargs):
        if 'path' not in kwargs.keys():
            kwargs['path'] = '/'.join(tp.getPhysicalPath())
        if 'sort_on' not in kwargs.keys():
            kwargs['sort_on'] = 'getObjPositionInParent'
        return self(**kwargs)

    def catalog_row(self, context, row_data):
        """Add new row data to catalog"""
        path = '%s/row-%s' % ('/'.join(context.getPhysicalPath()), row_data['__uuid__'])
        row_data['path'] = path
        self.catalog_object(CatalogDictWrapper(row_data, context, path), uid=path)

    security.declareProtected(manage_zcatalog_entries, 'catalog_object')
    def catalog_object(self, obj, uid=None, idxs=None, update_metadata=1,
                       pghandler=None):
        if not IIndexableObjectWrapper.providedBy(obj):
            obj = IndexableObjectWrapper(obj, self)
        super(TablePageCatalog,
              self).catalog_object(obj, uid=uid, idxs=idxs,
                                   update_metadata=update_metadata,
                                   pghandler=pghandler)

    security.declareProtected(manage_zcatalog_entries, 'uncatalog_row')
    def uncatalog_row(self, context, uid):
        """Remove a row from the catalog"""
        path = '%s/row-%s' % ('/'.join(context.getPhysicalPath()), uid)
        self.uncatalog_object(path)

    security.declareProtected(manage_zcatalog_entries, 'reindex_rows')
    def reindex_rows(self, context, uids, storage=None):
        """Reindex one of more rows using uuid information"""
        if isinstance(uids, basestring):
            uids = [uids]
        storage = storage or IDataStorage(context)
        for uid in uids:
            path = '%s/row-%s' % ('/'.join(context.getPhysicalPath()), uid)
            data = storage.get(uid)
            self.uncatalog_object(path)
            self.catalog_object(CatalogDictWrapper(data, context, path), uid=path)

    security.declareProtected(search_zcatalog, 'resolve_path')
    def resolve_path(self, path):
        # Override of original method: return the fake object
        # /Plone/path/to/tpage/row-uuid
        try:
            path_elements = path.split('/')
            tp_path = '/'.join(path_elements[:-1])
            uuid = path_elements[-1][4:]
            tp = self.unrestrictedTraverse(tp_path)
            storage = IDataStorage(tp)
            return CatalogDictWrapper(storage[uuid], tp, path)
        except Exception:
            # Very ugly, but Plone code does the same...
            pass

    security.declareProtected(manage_zcatalog_entries, 'manage_catalogRebuild')
    def manage_catalogRebuild(self, RESPONSE=None, URL1=None):
        """Clears the catalog and indexes all row of all table pages.
        This may take some time.
        """
        elapse = time.time()
        c_elapse = time.clock()

        self.clearFindAndRebuild()

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse

        if RESPONSE is not None:
            RESPONSE.redirect(
              URL1 + '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Rebuilt\n'
                           'Total time: %s\n'
                           'Total CPU time: %s'
                                % (repr(elapse), repr(c_elapse))))


    security.declareProtected(manage_zcatalog_entries, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """Empties catalog, then finds all tablepage objects and reindexes all rows.
           This may take some time.
        """
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        catalog = portal.portal_catalog
        pages = catalog(object_provides=ITablePage.__identifier__)
        for page in pages:
            obj = page.getObject()
            storage = IDataStorage(obj)
            for row in storage:
                if row.get('__label__'):
                    continue
                self.catalog_row(obj, row)

InitializeClass(TablePageCatalog)


# Let's clear broken ZMI tabs
tabs = list(TablePageCatalog.manage_options)
tabs = [x for x in tabs if x['label'] not in ('Find Objects', 'Query Report', 'Query Plan', 'Ownership', 'Actions', 'Overview')]
TablePageCatalog.manage_options = tuple(tabs)


class args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def manage_addTablePageCatalog(self, REQUEST=None):
    """Add the TablePage catalog"""

    c = TablePageCatalog()
    self._setObject(c.getId(), c)

    cat = getattr(self, c.getId())
    
    # Add Lexicon
    cat.manage_addProduct['ZCTextIndex'].manage_addLexicon(
        'pg_lexicon',
        elements=[
            args(group='Case Normalizer', name='Case Normalizer'),
            args(group='Stop Words', name=" Don't remove stop words"),
            args(group='Word Splitter', name="Unicode Whitespace splitter"),
        ]
        )
    
    # path index
    cat.addIndex('SearchableText', 'ZCTextIndex',
                 extra = args(doc_attr='SearchableText',
                              lexicon_id='pg_lexicon',
                              index_type='Okapi BM25 Rank')
                 )
    # SearchText index
    cat.addIndex('path', 'PathIndex')
    # getObjPositionInParent 
    cat.addIndex('getObjPositionInParent', 'FieldIndex')
    cat.addColumn('getObjPositionInParent')
    # getObjPositionInParent 
    cat.addIndex('Creator', 'FieldIndex')
    # UID
    cat.addColumn('UID')

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
