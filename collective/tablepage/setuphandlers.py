# -*- coding: utf-8 -*-

import uuid
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

def _uuid_all(context):
    logger.info("Generating uuids info for old rows")
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides=ITablePage.__identifier__)
    for brain in results:
        logger.info("Checking %s" % brain.getPath())
        obj = brain.getObject()
        storage = IDataStorage(obj)
        for row in storage:
            if not row.get('__uuid__'):
                new_uid = str(uuid.uuid4())
                logger.info(new_uid)
                row['__uuid__'] = new_uid
        logger.info("Done for %s" % brain.getPath())
    logger.info("uuid generation done")

def migrateTo04(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tablepage:to1100',)
    logger.info("Migrated to 0.4")

def migrateTo05(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'jsregistry')
    logger.info("Migrated to 0.5")

def migrateTo05b2(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tablepage:to1210')
    logger.info("Migrated to 0.5b2")

def migrateTo08(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'rolemap')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'cssregistry')
    createCatalog(portal)
    _uuid_all(context)
    logger.info("Now indexing all rows inside Table Page contents")
    portal.tablepage_catalog.clearFindAndRebuild()
    logger.info("...done")
    logger.info("Migrated to 0.8")

def migrateTo08b1(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    logger.info("Checking rows (or labels) without an uuid")
    _uuid_all(portal)
    logger.info("Adding new catalog columns")
    addCatalogColumns(portal, ['is_label', 'label'])
    logger.info("Now indexing all rows inside Table Page contents")
    portal.tablepage_catalog.clearFindAndRebuild()
    logger.info("...done")
    logger.info("Migrated to 0.8b1")

def migrateTo08b2(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    logger.info("Adding new catalog indexes")
    addCatalogIndex(portal, 'allowedRolesAndUsers', 'KeywordIndex')
    addCatalogIndex(portal, 'is_label')
    logger.info("Now indexing all rows inside Table Page contents")
    portal.tablepage_catalog.clearFindAndRebuild()
    logger.info("...done")
    logger.info("Migrated to 0.8b2")

def migrateTo08b3(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    logger.info("Removing useless catalog index allowedRolesAndUsers")
    try:
        portal.tablepage_catalog.delIndex('allowedRolesAndUsers')
        logger.info("Removed!")
    except CatalogError:
        logger.info("...not found: doing nothing")
    logger.info("Migrated to 0.8b3")

def migrateTo081(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    setup_tool = getToolByName(context, 'portal_setup')
    portal_javascripts = getToolByName(context, 'portal_javascripts')
    was_enabled = False
    resource = portal_javascripts.getResource('++resource++collective.tablepage.resources/jquery.dataTables.rowGrouping.js')
    if resource and resource.getEnabled():
        was_enabled = True
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'jsregistry')
    if was_enabled:
        logger.info("rowGroping plugin was enabled - re-activating with new configuration")
        portal_javascripts.getResource('++resource++collective.tablepage.resources/jquery.dataTables.rowGrouping.js').setEnabled(True)
        portal_javascripts.cookResources()
    logger.info("Migrated to 0.8.1")
