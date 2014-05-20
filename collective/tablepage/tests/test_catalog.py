# -*- coding: utf-8 -*-

import unittest
from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class TablePageCatalogTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page1', title="The Table Document")
        portal.table_page1.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                                              'type': 'String', 'vocabulary': '', 'options': []},
                                             {'id': 'col_b', 'label': 'Col B', 'description': '',
                                              'type': 'String', 'vocabulary': '', 'options': []}
        ])
        portal.invokeFactory(type_name='TablePage', id='table_page2', title="Another Table Document")        
        portal.table_page2.edit(pageColumns=[{'id': 'col_c', 'label': 'Col C', 'description': '',
                                              'type': 'String', 'vocabulary': '', 'options': []},
                                             {'id': 'col_b', 'label': 'Col B', 'description': '',
                                              'type': 'String', 'vocabulary': '', 'options': []}
        ])
        self.tp_catalog = portal.tablepage_catalog
        self.tp_catalog.addIndex(name='col_a', type='FieldIndex')

    def add_rows(self):
        portal = self.layer['portal']
        storage = IDataStorage(portal.table_page1)
        data = {'__creator__': 'user1', 'col_a': 'Lorem ipsum', '__uuid__': 'aaa'}
        storage.add(data)
        self.tp_catalog.catalog_row(portal.table_page1, data)
        data = {'__creator__': 'user1', 'col_a': 'dolor sit amet', '__uuid__': 'bbb'}
        storage.add(data)
        self.tp_catalog.catalog_row(portal.table_page1, data)
        # another TP
        storage = IDataStorage(portal.table_page2)
        data = {'__creator__': 'user1', 'col_a': 'consectetur adipisicing elit', '__uuid__': 'ccc'}
        storage.add(data)
        self.tp_catalog.catalog_row(portal.table_page2, data)
        data = {'__creator__': 'user1', 'col_a': 'sed do eiusmod tempor', '__uuid__': 'ddd'}
        storage.add(data)
        self.tp_catalog.catalog_row(portal.table_page2, data)

    def test_catalog_rows_on_add(self):
        portal = self.layer['portal']
        self.add_rows()
        storage = IDataStorage(portal.table_page1)
        self.assertEqual(len(self.tp_catalog()), 4)
        self.assertEqual(len(list(self.tp_catalog.searchTablePage(portal.table_page1))), 2)
        self.assertEqual(self.tp_catalog.searchTablePage(portal.table_page1)[0]._unrestrictedGetObject()['col_a'],
                         storage[0]['col_a'])

    def test_recatalog_rows_on_edit(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.add_rows()
        tp = portal.table_page1
        view = getMultiAdapter((tp, request), name='edit-record')
        request.form['row-index'] = 0
        request.form['form.submitted'] = '1'
        request.form['col_a'] = 'foo bar baz'
        view()
        self.assertEqual(len(self.tp_catalog()), 4)
        self.assertEqual(len(self.tp_catalog.searchTablePage(tp)), 2)
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[0]._unrestrictedGetObject()['col_a'],
                         'foo bar baz')

    def test_uncatalog_rows_on_delete(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.add_rows()
        tp = portal.table_page1
        view = getMultiAdapter((tp, request), name='delete-record')
        request.form['row-index'] = 0
        request.form['form.submitted'] = '1'
        view()
        self.assertEqual(len(self.tp_catalog()), 3)
        self.assertEqual(len(list(self.tp_catalog.searchTablePage(tp))), 1)
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[0]._unrestrictedGetObject()['col_a'],
                         'dolor sit amet')

    def test_update_catalog(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.add_rows()
        tp = portal.table_page1
        storage = IDataStorage(tp)
        storage[1]['col_a'] = 'foo bar baz'
        self.tp_catalog.manage_catalogReindex(request, request.response, self.tp_catalog.absolute_url())
        self.assertEqual(len(self.tp_catalog()), 4)
        self.assertEqual(len(self.tp_catalog.searchTablePage(tp)), 2)
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[1]._unrestrictedGetObject()['col_a'],
                         'foo bar baz')

    def test_rebuild_catalog(self):
        portal = self.layer['portal']
        request = self.layer['request']
        self.add_rows()
        tp = portal.table_page1
        storage = IDataStorage(tp)
        storage[1]['col_a'] = 'foo bar baz'
        self.tp_catalog.manage_catalogReindex(request, request.response, self.tp_catalog.absolute_url())
        self.assertEqual(len(list(self.tp_catalog())), 4)
        self.assertEqual(len(self.tp_catalog.searchTablePage(tp)), 2)
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[1]._unrestrictedGetObject()['col_a'],
                         'foo bar baz')
        
    def test_catalog_reindex_rows(self):
        portal = self.layer['portal']
        self.add_rows()
        tp = portal.table_page1
        storage = IDataStorage(tp)
        portal = self.layer['portal']
        data = {'__creator__': 'user1', 'col_a': 'Proin elementum', '__uuid__': 'ccc'}
        storage.add(data)
        self.tp_catalog.catalog_row(tp, data)
        self.assertEqual(len(list(self.tp_catalog.searchTablePage(tp))), 3)
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[0]._unrestrictedGetObject()['col_a'],
                         'Lorem ipsum')
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[1]._unrestrictedGetObject()['col_a'],
                         'dolor sit amet')
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[2]._unrestrictedGetObject()['col_a'],
                         'Proin elementum')
        data = storage.get('bbb')
        del storage['bbb']
        storage.add(data, 2)
        self.tp_catalog.reindex_rows(tp, ['bbb', 'ccc'])
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[1]._unrestrictedGetObject()['col_a'],
                         'Proin elementum')
        self.assertEqual(self.tp_catalog.searchTablePage(tp)[2]._unrestrictedGetObject()['col_a'],
                         'dolor sit amet')
