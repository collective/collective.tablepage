# -*- coding: utf-8 -*-

import unittest

from StringIO import StringIO
import os.path

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING

class FileFieldTestCase(unittest.TestCase):
    
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

    def test_file_creation_1(self):
        """Same file can be added multiple times when title is provided"""
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        with open(__file__) as f:
            file = StringIO(f.read())
        file.filename = os.path.basename(__file__)
        request.form['att'] = file
        request.form['title_att'] = "A python file"
        request.form['form.submitted'] = "1"
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        self.assertTrue('a-python-file' in folder.objectIds())
        file.seek(0)
        request.form['att'] = file
        request.form['title_att'] = "A python file"
        request.form['form.submitted'] = "1"
        view()
        self.assertTrue('a-python-file-1' in folder.objectIds())        
        file.seek(0)
        request.form['att'] = file
        request.form['title_att'] = "A python file"
        request.form['form.submitted'] = "1"
        request.form['title_att'] = "Another python file"        
        view()
        self.assertTrue('another-python-file' in folder.objectIds())

    def test_file_creation_2(self):
        """When title is not provided, file id is used and we can't add multiple files (same as Plone)"""
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        with open(__file__) as f:
            file = StringIO(f.read())
        filename = os.path.basename(__file__)
        file.filename = filename
        request.form['att'] = file
        request.form['form.submitted'] = "1"
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        file_content = folder[filename]
        self.assertTrue(file_content.getId() in folder.objectIds())
        self.assertEqual(len(folder.objectIds()), 2)
        file.seek(0)
        request.form['att'] = file
        request.form['form.submitted'] = "1"
        view()
        # we still have two files
        self.assertEqual(len(folder.objectIds()), 2)
        storage = IDataStorage(tp)
        self.assertEqual(storage[0]['att'], storage[1]['att'])
        

class MultipleFileFieldTestCase(unittest.TestCase):
    
    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        wtool = portal.portal_workflow
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='Folder', id='folder', title="Attachment storage")
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.folder.invokeFactory(type_name='File', id='attachment1', title="An attachment")
        portal.folder.invokeFactory(type_name='File', id='attachment2', title="Another attachment")
        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'att', 'label': 'Attachments', 'description': '',
                              'type': 'Files', 'vocabulary': ''}],
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
        self.assertTrue('An attachment' in view())
        self.assertTrue('Another attachment' in view())

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
        self.assertTrue('An attachment' in view())

    def test_no_access(self):
        """Contributor can't add or select any file without permissions of the storage folder"""
        portal = self.layer['portal']
        tp = portal.table_page
        tp.manage_setLocalRoles('user0', ('Contributor',))
        login(portal, 'user0')
        view = tp.restrictedTraverse('@@edit-record')
        self.assertTrue('Upload a new document' not in view())
        self.assertTrue('An attachment' not in view())
        self.assertTrue('Seems you have no permission to access the file storage' in view())

    def test_view_forbidden_attachment(self):
        """Although attachment is not accessible, normal table visitor can see the link"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user0', 'att': '\n'.join([folder.attachment1.UID(), folder.attachment2.UID()])})
        logout()
        self.assertTrue('An attachment' in tp())
        self.assertTrue('Another attachment' in tp())

    def test_files(self):
        """Can generato more than one attachent in the same request"""
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        with open(__file__) as f:
            file1 = StringIO(f.read())
        with open(__file__) as f:
            file2 = StringIO(f.read())
        file1.filename = os.path.basename(__file__)
        file2.filename = os.path.basename(__file__)

        request.form['att_0'] = file1
        request.form['title_att_0'] = "A python file"
        request.form['att_1'] = file2
        request.form['title_att_1'] = "Another python file"
        request.form['form.submitted'] = "1"
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        self.assertTrue('a-python-file' in folder.objectIds())
        self.assertTrue('another-python-file' in folder.objectIds())

