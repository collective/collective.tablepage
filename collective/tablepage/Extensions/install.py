# -*- coding: utf-8 -*-

from collective.tablepage import logger

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-collective.tablepage:uninstall')
        logger.info("Uninstalled")
