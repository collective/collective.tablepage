# -*- coding: utf-8 -*-

from collective.tablepage import logger
from Products.CMFCore.utils import getToolByName

def migrateTo04(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tablepage:to1100',)
    logger.info("Migrated to 0.4")

def migrateTo05(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile('profile-collective.tablepage:default', 'jsregistry')
    logger.info("Migrated to 0.5")