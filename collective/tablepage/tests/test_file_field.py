# -*- coding: utf-8 -*-

import unittest

from zope import interface
from zope.component import queryUtility
from AccessControl import Unauthorized

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING

class SecurityTestCase(unittest.TestCase):
    
    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        wtool = portal.portal_workflow
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='Folder', id='folder', title="Attachment storage")
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.folder.invokeFactory(type_name='File', id='attachment', title="An ancient attachment")
        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'att', 'label': 'Attachment', 'description': '',
                              'type': 'File', 'vocabulary': ''}],
                attachmentStorage=portal.folder.UID())
        wtool.doActionFor(tp, 'publish')

    def test_full_access(self):
        """Contributor can add new files inside the storage folder and also select existings ones"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        folder.manage_setLocalRoles('user0', ('Contributor',))
        folder.reindexObjectSecurity()
        # portal.portal_workflow.doActionFor(folder, 'publish')
        login(portal, 'user0')
        view = tp.restrictedTraverse('@@edit-record')
        self.assertTrue('Upload a new document' in view())
        self.assertTrue('An ancient attachment' in view())

    def test_selection_only_access(self):
        """Contributor can't add new files if he doesn't have permission on the folder, but he can still select"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        folder.manage_setLocalRoles('user0', ('Reader',))
        folder.reindexObjectSecurity()
        login(portal, 'user0')
        view = tp.restrictedTraverse('@@edit-record')
        self.assertTrue('Upload a new document' not in view())
        self.assertTrue('An ancient attachment' in view())

    def test_no_access(self):
        """Contributor can't add or select any file without permissions of the storage folder"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        login(portal, 'user0')
        view = tp.restrictedTraverse('@@edit-record')
        self.assertTrue('Upload a new document' not in view())
        self.assertTrue('An ancient attachment' not in view())
        self.assertTrue('Seems you have no permission to access the file storage' in view())

    def test_view_forbidden_attachment(self):
        """Although attachment is not accessible, normal table visitor can see the link"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user0', 'att': folder.attachment.UID()})
        logout()
        self.assertTrue('An ancient attachment' in tp())
