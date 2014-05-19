# -*- coding: utf-8 -*-

import transaction
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.tablepage import config
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage import logger
from collective.tablepage.interfaces import IDataStorage
from zope.component import getMultiAdapter


class RefreshSearchView(BrowserView):
    """Refresh rows indexed"""

    def __call__(self, *args, **kwargs):
        context = self.context
        request = self.request
        catalog = getToolByName(context, config.CATALOG_ID)
        storage = IDataStorage(context)
        uuids = []
#        # now we load the tabel view and rebuild all rows by using the ignore_cache parameter
#        table_view = getMultiAdapter((context, request), name=u'view-table')
#        table_view.rows(ignore_cache=True)
        for index, row in enumerate(storage):
            uuid = row.get('__uuid__')
            if uuid:
                catalog.reindex_rows(context, uuid)
            if index % 100 == 0:
                logger.info("Refreshing catalog and cached (%d)" % index)
                transaction.savepoint()
        getToolByName(context, 'plone_utils').addPortalMessage(_('reindex_performed_message',
                                                                 u'$count rows has been updated',
                                                                 mapping={'count': index}))
        request.response.redirect('%s/edit-table' % context.absolute_url())
