# -*- coding: utf-8 -*-

import unittest

from Products.CMFCore.utils import getToolByName
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from zope.component import getMultiAdapter


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
                              'type': 'String', 'vocabulary': '', 'options': []}])
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
                              'type': 'String', 'vocabulary': '', 'options': []}])
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'F\xc3\xb2\xc3\xb2 data from user1'})
        adapter = getMultiAdapter((tp, self.layer['request']), interface=IColumnField, name=u'String')
        adapter.configuration = tp.getPageColumns()[0]
        try:
            adapter.render_edit('F\xc3\xb2\xc3\xb2 data from user1')
        except UnicodeDecodeError:
            self.fail("getText() raised UnicodeDecodeError unexpectedly!")

    def test_emtpy_table(self):
        """Prevent regression om Plone 4.2 and below: empty table should display proper message""" 
        portal = self.layer['portal']
        request = self.layer['request']
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': 'Th\xc3\xacs data is futile',
                              'type': 'String', 'vocabulary': '', 'options': []}])
        view = getMultiAdapter((tp, request), name='tablepage-edit')
        self.assertTrue('No rows' in view())


class RefreshViewTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []}])
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'Lorem', '__uuid__': 'aaa'})
        storage.add({'__creator__': 'user1', 'col_a': 'Ipsum', '__uuid__': 'bbb'})
        storage.add({'__creator__': 'user1', 'col_a': 'Sit', '__uuid__': 'ccc'})
        self.tp_catalog = getToolByName(portal, 'tablepage_catalog')

    def test_refreshing(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp_catalog = self.tp_catalog
        self.assertEqual(len(tp_catalog.searchTablePage(portal.table_page)), 0)
        view = getMultiAdapter((portal.table_page, request), name=u'refresh-catalog')
        view()
        self.assertEqual(len(tp_catalog.searchTablePage(portal.table_page)), 3)


