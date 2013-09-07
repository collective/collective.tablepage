# -*- coding: utf-8 -*-

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
        return self._ann[index]

    def __delitem__(self, index):
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
