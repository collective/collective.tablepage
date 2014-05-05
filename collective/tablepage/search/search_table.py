# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.search.interfaces import ISearchableColumn
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getUtilitiesFor


class SearchTableViewlet(ViewletBase):
    """A viewlet that display a search form for data in table"""

    @property
    def view_name(self):
        # remove this uglyness when Plone 3 will be removed and we ere able to
        # define our basic view for tablepage
        if self.view.__name__=='plone':
            return ''
        return '@@' + self.view.__name__

    def get_valid_catalog_indexes(self):
        """Look for TablePage portal catalog configuration"""
        context = self.context
        tp_catalog = getToolByName(context, 'tablepage_catalog')
        index_ids = tp_catalog.indexes()
        indexes = {}
        for conf in context.getSearchConfig():
            if not conf:
                continue
            field_id = conf['id']
            if field_id not in index_ids:
                continue
            indexes[field_id] = tp_catalog.Indexes[field_id]
        return indexes

    def search_fields(self):
        """Return a set of search field to be rendered"""
        context = self.context
        utilities = {}
        tableConf = {}
        
        # All registered search fields
        for name, ut in getUtilitiesFor(ISearchableColumn):
            utilities[name] = ut
        # table configuration
        for conf in context.getPageColumns():
            tableConf[conf['id']] = conf

        catalog_keys = self.get_valid_catalog_indexes()

        fields = []
        for conf in context.getSearchConfig():
            if not conf:
                continue
            field_id = conf['id']
            if field_id=='SearchableText':
                field_type = 'Text'
            else:
                field_type = tableConf[field_id]['type']
            if field_type not in utilities.keys() or field_id not in catalog_keys.keys():
                continue
            field = utilities[field_type]
            field.id = field_id
            field.configuration = tableConf.get(field_id) or {}
            field.search_configuration = conf
            field.context = context
            field.request = self.request
            field.label = conf.get('label') or field.configuration.get('label') or _(u'Search in text')
            field.description = conf.get('description') or field.configuration.get('description') or ''
            fields.append(field.render(meta_type=catalog_keys[field_id].meta_type))
        return fields
