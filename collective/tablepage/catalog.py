# -*- coding: utf-8 -*-

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import search_zcatalog
from AccessControl.Permissions import manage_zcatalog_entries
from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from plone.indexer.wrapper import IIndexableObjectWrapper
from plone.indexer.wrapper import IndexableObjectWrapper
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage import config
from zope.interface import Interface, implements


class ICatalogDictWrapper(Interface):
    pass

class CatalogDictWrapper(object):
    implements(ICatalogDictWrapper)
    
    def __init__(self, dict_obj):
        for k,v in dict_obj.items():
            if k.startswith('__'):
                continue
            self.__setattr__(k, v)


class TablePageCatalog(CatalogTool):
    """Rows catalog for Table page"""

    id = config.CATALOG_ID
    title = "TablePage Catalog"

    security = ClassSecurityInfo()

    def __init__(self):
        ZCatalog.__init__(self, self.getId(), self.title)

    def index_row(self, context, row_data):
        path = '/'.join(context.getPhysicalPath()) + '/' + row_data['__uuid__']
        row_data['path'] = path
        self.catalog_object(CatalogDictWrapper(row_data), uid=path)

    security.declareProtected(manage_zcatalog_entries, 'catalog_object')
    def catalog_object(self, obj, uid=None, idxs=None, update_metadata=1,
                       pghandler=None):
        if not IIndexableObjectWrapper.providedBy(obj):
            obj = IndexableObjectWrapper(obj, self)
        super(TablePageCatalog,
              self).catalog_object(obj, uid=uid, idxs=idxs,
                                   update_metadata=update_metadata,
                                   pghandler=pghandler)

    security.declareProtected(search_zcatalog, 'resolve_path')
    def resolve_path(self, path):
        # Override of original method: return the fake object
        try:
            path_elements = path.split('/')
            tp_path = '/'.join(path_elements[:-1])
            uuid = path_elements[-1]
            tp = self.unrestrictedTraverse(tp_path)
            storage = IDataStorage(tp)
            return CatalogDictWrapper(storage[uuid])
        except Exception:
            pass

InitializeClass(TablePageCatalog)


# Let's clear broken ZMI tabs
tabs = list(TablePageCatalog.manage_options)
tabs = [x for x in tabs if x['label'] not in ('Find Objects', 'Query Report', 'Query Plan')]
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

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
