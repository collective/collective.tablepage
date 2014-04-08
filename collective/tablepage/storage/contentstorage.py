# -*- coding: utf-8 -*-

from AccessControl import allow_class
from persistent.list import PersistentList
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from collective.tablepage.interfaces import IDataStorage

STORAGE_KEY = "table_page_storage"


class DataStorage(object):
    """Store data inside the Plone content
    Data are stored as primitive types in the content annotations structure
    """ 
    implements(IDataStorage)

    def __init__(self, context):
        self.context = context
        self._ann = self._initStructure()
    
    def _initStructure(self):
        """
        Data is stored in the object's annotations.
        Create the structure or return it
        """
        ann = IAnnotations(self.context)
        if not STORAGE_KEY in ann.keys():
            ann[STORAGE_KEY] = PersistentList()
        return ann[STORAGE_KEY]

    def __repr__(self):
        return "<DataStorage [%s]>" % str(", ".join(["<%s>" % d.items() for d in self._ann]))

    def __getitem__(self, index):
        if isinstance(index, basestring):
            for row in self._ann:
                if row.get('__uuid__') == index:
                    return row
        return self._ann[index]

    def get(self, index):
        """Safe getter for restricted python. Return a primitive dict, not a persistent"""
        if isinstance(index, basestring):
            for row in self._ann:
                if row.get('__uuid__') == index:
                    return row.__dict__['data'].copy()
        return self._ann[index].__dict__['data'].copy()

    def __delitem__(self, index):
        if isinstance(index, basestring):
            for pos, row in enumerate(self._ann):
                if row.get('__uuid__') == index:
                    del self._ann[pos]
                    return
        del self._ann[index]

    def __len__(self):
        return len(self._ann)

    def clear(self):
        """Clear all storage data"""
        ann = IAnnotations(self.context)
        del ann[STORAGE_KEY]

    def add(self, data, index=-1):
        """Add data to the storage. Data must the a dict-like structure"""
        row = PersistentDict()
        row.update(data)
        if index>-1:
            self._ann.insert(index, row)
        else:
            self._ann.append(row)

    def update(self, index, data):
        self._ann[index].update(data)

    def nullify(self, index, key):
        try:
            del self._ann[index][key]
        except KeyError:
            pass

allow_class(DataStorage)
