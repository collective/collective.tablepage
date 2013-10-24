# -*- coding: utf-8 -*-

import unittest

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING

class ViewTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)

    def test_encoding(self):
        """Be sure that we have no problems with non-ASCII chars"""
        portal = self.layer['portal']
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(textBefore='<p>L\xc3\xb2r\xc3\xa8m Ips\xc3\xb9m</p>',
                pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': 'Th\xc3\xacs data is futile',
                              'type': 'String', 'vocabulary': ''}])
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'F\xc3\xb2\xc3\xb2 data from user1'})
        try:
            tp.getText()
        except UnicodeDecodeError:
            self.fail("getText() raised UnicodeDecodeError unexpectedly!")

    def test_encoding_on_rendering(self):
        """Be sure that we have no problems with non-ASCII chars"""
        portal = self.layer['portal']
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(textBefore='<p>L\xc3\xb2r\xc3\xa8m Ips\xc3\xb9m</p>',
                pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': 'Th\xc3\xacs data is futile',
                              'type': 'String', 'vocabulary': ''}])
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'F\xc3\xb2\xc3\xb2 data from user1'})
        adapter = getMultiAdapter((tp, self.layer['request']), interface=IColumnField, name=u'String')
        adapter.configuration = tp.getPageColumns()[0]
        try:
            adapter.render_edit('F\xc3\xb2\xc3\xb2 data from user1')
        except UnicodeDecodeError:
            self.fail("getText() raised UnicodeDecodeError unexpectedly!")

        
