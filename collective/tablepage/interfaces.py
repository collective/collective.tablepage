# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute
from Products.ATContentTypes.interface.document import IATDocument


class ITablePage(IATDocument):
    """A document with an editable table"""


class IColumnField(Interface):
    """An object able to render an widget for handling data from a column"""
    
    configuration = Attribute("""Columns configuration""")
    cache_time = Attribute("""Integer value, in seconds, for determining if and how the column render will be cached""")

    def render_edit(data):
        """
        Get the HTML field for editing. This can be None, and the field will not be rendered on editing row
        """
    
    def render_view(data, index=None):
        """Get the HTML field for final display
        @index the row index of the data in the table
        """


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

    def nullify(index, key):
        """Delete a single row subitem"""


class IColumnDataRetriever(Interface):
    """An object that can handle data stored (or to be stored) inside the IDataStorage"""

    def get_from_request(name, request):
        """Read data from the request and return a {id: value} dict, or None"""

    def data_for_display(data, backend=False, row_index=None):
        """Transform data, to be displayed outside Plone
        @backend specify that data is for backend purpose
        @row_index index of the row were extraction is taking place
        """

    def data_to_storage(data):
        """Sanitize data that will be saved to storage"""
    

class IFieldValidator(Interface):
    """A validator for the submitted data"""
    
    def validate(configuration, data=None):
        """Validate input data
        @param configuration TablePage configuration
        @data data to be validated (commonly taken from the request)        
        @return the error message (if any) or None
        """

