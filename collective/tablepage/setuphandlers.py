# -*- coding: utf-8 -*-

from collective.tablepage import logger
from collective.tablepage import config
from collective.tablepage.interfaces import ITablePage
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.catalog import manage_addTablePageCatalog
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.Catalog import CatalogError


def createCatalog(portal):
    if not hasattr(portal, config.CATALOG_ID):
        manage_addTablePageCatalog(portal)
        logger.info('Added the catalog')
    else:
        logger.info('Catalog found. Skipping...')

def addCatalogColumns(portal, columns):
    catalog = portal.tablepage_catalog
    for c in columns:
        logger.info("Adding column %s" % c)
        try:
            catalog.addColumn(c)
        except CatalogError:
            logger.info("Column %s already exists" % c)

def addCatalogIndex(portal, name, type="FieldIndex"):
    catalog = portal.tablepage_catalog
    logger.info("Adding index %s (%s)" % (name, type))
    try:
        catalog.addIndex(name, type)
    except CatalogError:
        logger.info("... already exists: skipping")

def setupVarious(context):
    if context.readDataFile('collective.tablepage_various.txt') is None:
        return

    portal = context.getSite()
    createCatalog(portal)

