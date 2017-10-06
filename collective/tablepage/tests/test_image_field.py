# -*- coding: utf-8 -*-

import unittest

from StringIO import StringIO
import os.path

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING

IMAGE_FILE_PATH = os.path.dirname(__file__) + '/logo-home.png'


class ImageFieldTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        wtool = portal.portal_workflow
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='Folder', id='folder', title="Attachment storage")
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.folder.invokeFactory(type_name='Image', id='attachment', title="An ancient attachment")
        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'att', 'label': 'Attachment', 'description': '',
                              'type': 'Image', 'vocabulary': '', 'options': []}],
                attachmentStorage=portal.folder.UID())
        wtool.doActionFor(tp, 'publish')

    def test_full_access(self):
        """Contributor can add new images inside the storage folder and also select existings ones"""
        portal = self.layer['portal']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        folder.manage_setLocalRoles('user0', ('Contributor',))
        folder.reindexObjectSecurity()
        # portal.portal_workflow.doActionFor(folder, 'publish')
        login(portal, 'user0')
        view = tp.restrictedTraverse('@@edit-record')
        self.assertTrue('Upload a new image' in view())
        self.assertTrue('An ancient attachment' in view())

    def test_image_creation_1(self):
        """Same image can be added multiple times when title is provided"""
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        folder = portal.folder
        tp.manage_setLocalRoles('user0', ('Contributor',))
        with open(IMAGE_FILE_PATH) as f:
            file = StringIO(f.read())
        file.filename = os.path.basename(IMAGE_FILE_PATH)
        request.form['att'] = file
        request.form['title_att'] = "A python image"
        request.form['form.submitted'] = "1"
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        self.assertTrue('a-python-image' in folder.objectIds())
        file.seek(0)
        request.form['att'] = file
        request.form['title_att'] = "A python image"
        request.form['form.submitted'] = "1"
        view()
        self.assertTrue('a-python-image-1' in folder.objectIds())
        file.seek(0)
        request.form['att'] = file
        request.form['title_att'] = "A python image"
        request.form['form.submitted'] = "1"
        request.form['title_att'] = "Another python image"
        view()
        self.assertTrue('another-python-image' in folder.objectIds())

    def test_size_option(self):
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Image', id='image', title="An image")

        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'att', 'label': 'Attachment', 'description': '',
                              'type': 'Image', 'vocabulary': 'size:icon', 'options': []}],
                attachmentStorage=portal.folder.UID())

        storage = IDataStorage(tp)
        storage.add({'__creator__': TEST_USER_NAME, 'att': portal.image.UID(),
                     '__uuid__': 'aaa'})

        output = tp()
        self.assertTrue(u'<img src="resolveuid/' + portal.image.UID() + u'/image_icon"' in output)
