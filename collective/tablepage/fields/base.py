# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
from collective.tablepage.interfaces import IColumnDataRetriever
from zope.schema.interfaces import IVocabularyFactory


class BaseField(object):
    """Generic helper class for all fields"""

    # not implemented; subclasses must change this
    edit_template = None
    view_template = None
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = None
        self.configuration = None

    def render_edit(self, data):
        data = data or ''
        if isinstance(data, basestring):
            # on validation error we can get a FileUpload instance
            self.data = data.decode('utf-8')
        return self.edit_template(data=self.data)

    def render_view(self, data):
        self.data = data or ''
        return self.view_template(data=self.data)

    def _get_obj_info(self, uuid):
        # for fields that need to refer to other contents
        rcatalog = getToolByName(self.context, 'reference_catalog')
        obj = rcatalog.lookupObject(uuid)
        if obj:
            return dict(title=obj.Title() or obj.getId(),
                        url=obj.absolute_url(),
                        description=obj.Description(),
                        icon=obj.getIcon(relative_to_portal=1))
        return None

    @property
    def options(self):
        """Read configuration options as dict"""
        factory = getUtility(IVocabularyFactory, 'collective.tablepage.vocabulary.row_options')
        vocabulary = factory(self.context)

        options = {}
        for term in vocabulary:
            options[term.value] = term.value in self.configuration.get('options')
        return options


class BaseFieldDataRetriever(object):
    """Get data from the request, return it. Nothing more"""

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        if request.get(name) is not None:
            return {name: request.get(name)}
        return None

    def data_for_display(self, data, backend=False):
        """Default implementation... just return data""" 
        return data

    def data_to_storage(self, data):
        """Default implementation... just return data (stripped)"""
        return data and data.strip() or None
