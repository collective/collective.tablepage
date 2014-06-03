# -*- coding: utf-8 -*-

import unittest

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class BatchingTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'foo_field', 'label': 'Foo field', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              ],
                batchSize=10)
        self.tp = tp
        self.storage = IDataStorage(tp)

    def _addRows(self, nrows):
        for x in range(nrows):
            self.storage.add({'foo_field': '(Row data %d)' % (x+1)})

    def test_batching_disabled(self):
        tp = self.tp
        self._addRows(35)
        tp.setBatchSize(0)
        output = tp()
        self.assertTrue('(Row data 1)' in output)
        self.assertTrue('(Row data 35)' in output)

    def test_batching(self):
        tp = self.tp
        self._addRows(35)
        output = tp()
        self.assertTrue('(Row data 1)' in output)
        self.assertTrue('(Row data 11)' not in output)

    def test_batching_page2(self):
        tp = self.tp
        self._addRows(35)
        request = self.layer['request']
        request.form['b_start'] = 10
        output = tp()
        self.assertTrue('(Row data 1)' not in output)
        self.assertTrue('(Row data 11)' in output)

    def test_batching_label_at_first_page(self):
        tp = self.tp
        self._addRows(35)
        self.storage.add({'__label__': 'The Label'}, 0)
        output = tp()
        self.assertTrue('(Row data 1)' in output)
        self.assertTrue('The Label' in output)
        self.assertTrue(output.find('The Label') < output.find('(Row data 1)'))

    def test_batching_label_at_previous_page(self):
        tp = self.tp
        self._addRows(35)
        request = self.layer['request']
        self.storage.add({'__label__': 'The First Label'}, 3)
        self.storage.add({'__label__': 'The Second Label'}, 15)
        request.form['b_start'] = 10
        output = tp()
        self.assertTrue('(Row data 10)' in output)
        self.assertTrue('The First Label' in output)
        self.assertTrue('The Second Label' in output)
        self.assertTrue(output.find('The First Label') < output.find('(Row data 10)') < output.find('The Second Label'))

