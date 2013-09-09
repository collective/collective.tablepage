# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.interfaces import IColumnDataRetriever

class BaseField(object):
    """Generic helper class for all fields"""

    # not implemente; subclasses must change this
    edit_template = None
    view_template = None
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = None
        self.configuration = None

    def render_edit(self, data):
        self.data = data or ''
        return self.edit_template(data=data)

    def render_view(self, data):
        self.data = data or ''
        return self.view_template(data=data)


class BaseFieldDataRetriever(object):
    """Get data from the request, return it. Nothing more"""

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        if request.get(name) is not None:
            return {name: request.get(name)}
        return None

    def data_for_display(self, data):
        """Default implementation... just return data""" 
        return data
