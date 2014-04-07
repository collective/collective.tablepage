# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from collective.tablepage.config import MANAGE_SEARCH_PERMISSION
from collective.tablepage import tablepageMessageFactory as _


def checkSearchConfig(context, event):
    """Warn user if tablepage_catalog configuration is not proper"""
    sm = getSecurityManager()
    if not sm.checkPermission(MANAGE_SEARCH_PERMISSION, context):
        return
    tp_catalog = getToolByName(context, 'tablepage_catalog')
    indexes = tp_catalog.indexes()
    warn_fields = []
    for conf in context.getSearchConfig():
        if conf['id'] not in indexes:
            warn_fields.append(conf['id'])
    if warn_fields:
        putils = getToolByName(context, 'plone_utils')
        putils.addPortalMessage(_('bad_configured_search_cols',
                                  default=u"There are columns ($cols) defined as searchable but no indexes "
                                          u"with same has been found in the tablepage_catalog tool.\n"
                                          u"Search form will use them.",
                                  mapping={'cols': ', '.join(warn_fields)}),
                                type="warning")
