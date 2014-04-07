# -*- coding: utf-8 -*-

from collective.tablepage import logger
from collective.tablepage import config
from collective.tablepage.catalog import manage_addTablePageCatalog
from Products.CMFCore.utils import getToolByName

def createCatalog(portal):
    if not hasattr(portal, config.CATALOG_ID):
        manage_addTablePageCatalog(portal)
        logger.info('Added the catalog')
    else:
        logger.info('Catalog found. Skipping...')

def setupVarious(context):
    if context.readDataFile('collective.tablepage_various.txt') is None:
        return

    portal = context.getSite()
    createCatalog(portal)

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
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'rolemap')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'cssregistry')
    createCatalog(context)
    logger.info("Now indexing all rows inside Table Page contents")
    context.tablepage_catalog.clearFindAndRebuild()
    logger.info("...done")
    logger.info("Migrated to 0.8")
