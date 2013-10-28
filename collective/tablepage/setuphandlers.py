# -*- coding: utf-8 -*-

from collective.tablepage import logger
from Products.CMFCore.utils import getToolByName

def migrateTo04(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tablepage:to1100',)
    logger.info("Migrated to 0.4")
