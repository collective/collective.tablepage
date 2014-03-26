# -*- coding: utf-8 -*-

from Products.PageTemplates import Expressions
from collective.tablepage import logger
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.computed.interfaces import IComputedColumnHandler
from collective.tablepage.fields.interfaces import IComputedColumnField
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.interfaces import IDataStorage
from plone.memoize import instance
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements
from zope.tales.tales import CompilerError

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class ComputedBase(object):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_row_data(self, row):
        """Return a dict of data taken from other row values"""
        results = {}
        utils = {}
        configuration = self.context.getPageColumns()
        for col_index, conf in enumerate(configuration):
            col_type = conf['type']

            # let's cache (or use cached) utility
            cache = IAnnotations(self.request)
            cached = cache.get('colum-handle-%s' % col_type)
            if not cached:
                try:
                    utils[col_type] = getUtility(IComputedColumnHandler, name=col_type)
                except ComponentLookupError:
                    utils[col_type] = getUtility(IComputedColumnHandler)
                cache['colum-handle-%s' % col_type] = utils[col_type]
            else:
                utils[col_type] = cached

            if not col_type or col_type=='Computed':
                continue
            id = configuration[col_index]['id']
            data = row.get(id) or None

            results[id] = utils[col_type](data)
        return results

    def eval_mappings(self, index):
        """Compute mappings for TAL evaluation"""
        storage = IDataStorage(self.context)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        current_row = self._get_row_data(storage[index])
        return {'row': current_row,
                'rows': storage,
                'index': index,
                'portal': portal_state.portal(),
                'context': self.context,
                'request': self.request,
                }


class ComputedField(BaseField, ComputedBase):
    implements(IComputedColumnField)

    # not displayed on edit
    edit_template = None
    view_template = ViewPageTemplateFile('../templates/string_view.pt')

    @property
    @instance.memoize
    def cache_time(self):
        """
        The cache_time attribute here is computed.
        Look at the column configuration, second line, for a "cache:X" value, then
        cache use X as cache
        """
        conf = self.configuration.get('vocabulary') or ''
        conf = conf.splitlines()
        cache_time = [l for l in conf if l.startswith('cache:')]
        if cache_time:
            try:
                return int(cache_time[0][6:])
            except ValueError:
                logger.warning('Invalid column cache value: %s' % cache_time[0][6:])
        return 0

    def __init__(self, context, request):
        BaseField.__init__(self, context, request)

    def render_edit(self, data):
        """Will not render anything on edit"""
        return None

    def render_view(self, foo, index):
        """Whatever dummy value we receive, the result will be a TAL expression evaluation"""
        self.data = None
        expression = self.configuration.get('vocabulary')
        if expression:
            expression = expression.splitlines()[0]
            talEngine = Expressions.getEngine()
            compiledExpr = talEngine.compile(expression)
            try:
                self.data = compiledExpr(talEngine.getContext(self.eval_mappings(index=index)))
            except CompilerError:
                logger.debug("Can't evaluate %s" % expression)
                self.data = None
            except Exception:
                logger.debug("Error evaluating %s or row %d" % (expression, index))
                self.data = None
        return self.view_template(data=self.data)


class ComputedDataRetriever(ComputedBase):
    """Get data computing the TAL expression"""
    implements(IColumnDataRetriever)

    def __init__(self, context):
        ComputedBase.__init__(self, context, context.REQUEST)

    def get_from_request(self, name, request):
        raise NotImplementedError("ComputedColumn will not read anything from request")

    def data_for_display(self, foo, backend=False, row_index=None):
        """Data is always ignored""" 
        if backend:
            raise NotImplementedError("ComputedColumn will not output anything for backend mode")
        expression = self.configuration.get('vocabulary')
        if expression:
            expression = expression.splitlines()[0]
            talEngine = Expressions.getEngine()
            compiledExpr = talEngine.compile(expression)
            try:
                data = compiledExpr(talEngine.getContext(self.eval_mappings(index=row_index)))
            except CompilerError:
                logger.debug("Can't evaluate %s" % expression)
                data = None
            except Exception:
                logger.debug("Error evaluating %s or row %d" % (expression, row_index))
                data = None
        return data

    def data_to_storage(self, data):
        raise NotImplementedError("ComputedColumn will not save anything in the storage")
