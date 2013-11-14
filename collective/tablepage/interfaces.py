# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute
#from Products.ATContentTypes.interface.interfaces import ITextContent
from Products.ATContentTypes.interface.document import IATDocument

class ITablePage(IATDocument):
    """A document with an editable table"""


class IColumnField(Interface):
    """An object able to render an widget for handling data from a column"""
    
    configuration = Attribute("""Columns configuration""")

    def render_edit(data):
        """Get the HTML field for editing"""
    
    def render_view(data):
        """Get the HTML field for final display"""


class IDataStorage(Interface):
    """An object able to store table data inside Plone contents"""

    def __getitem__(index):
        """Get an item from the storage, by index"""

    def __delitem__(index):
        """Delete an item from the storage, by index"""

    def __len__():
        """Items in the storage"""

    def clear():
        """Clear all storage data"""

    def add(data, index=-1):
        """Add data to the storage. Data must the a dict-like structure"""

    def update(index, data):
        """Update data stored at given row"""


class IColumnDataRetriever(Interface):
    """An object that can handle data stored (or to be stored) inside the IDataStorage"""

    def get_from_request(name, request):
        """Read data from the request and return a {id: value} dict, or None"""

    def data_for_display(data, backend=False):
        """Transform data, to be displayed outside Plone
        @backend specify that data is for backend purpose
        """

    def data_to_storage(self, data):
        """Validate data that will be saved to storage"""
