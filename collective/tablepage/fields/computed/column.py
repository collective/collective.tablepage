# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.PageTemplates import Expressions
from collective.tablepage import logger
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.computed.interfaces import IComputedColumnHandler
from collective.tablepage.fields.interfaces import IComputedColumnField
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.interfaces import IDataStorage
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements
from zope.tales.tales import CompilerError

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class ComputedField(BaseField):
    implements(IComputedColumnField)

    # not displayed on edit
    edit_template = None
    view_template = ViewPageTemplateFile('../templates/string_view.pt')

    def render_edit(self, data):
        """Will not render anything on edit"""
        return None

    def render_view(self, foo, index):
        """Whatever dummy value we receive, the result will be a TAL expression evaluation"""
        self.data = None
        vocabulary = self.configuration.get('vocabulary')
        if vocabulary:
            talEngine = Expressions.getEngine()
            compiledExpr = talEngine.compile(vocabulary)
            try:
                self.data = compiledExpr(talEngine.getContext(self.eval_mappings(index=index)))
            except CompilerError:
                logger.debug("Can't evaluate %s" % vocabulary)
        return self.view_template(data=self.data)

    def _get_row_data(self, row):
        """Return a dict of data taken from other row values"""
        results = {}
        adapters = {}

        # let's cache adapters
        for conf in self.context.getPageColumns():
            col_type = conf['type']
            try:
                adapters[col_type] = getAdapter(self, IComputedColumnHandler, name=col_type)
            except ComponentLookupError:
                adapters[col_type] = IComputedColumnHandler(self)

        for k, v in row.items():
            # BBB:
            ctype = v.get('type')
            if not ctype or ctype=='Computed':
                continue
        return results

    def eval_mappings(self, index):
        """Compute mappings for TAL evaluation"""
        storage = IDataStorage(self.context)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        current_row = self._get_row_data(storage[index])
        return {'row': current_row,
                'portal': portal_state.portal(),
                'context': self.context,
                'request': self.request,
                }


class ComputedDataRetriever(object):
    """Get data computing the TAL expression"""

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context

    def get_from_request(self, name, request):
        raise NotImplementedError("ComputedColumn will not read anything from request")

    def data_for_display(self, data, backend=False):
        """Just display the data""" 
        if backend:
            raise NotImplementedError("ComputedColumn will not output anything for backend mode")
        return data

    def data_to_storage(self, data):
        raise NotImplementedError("ComputedColumn will not save anything in the storage")
