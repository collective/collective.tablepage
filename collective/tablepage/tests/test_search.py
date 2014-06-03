# -*- coding: utf-8 -*-

import unittest
from collective.tablepage.catalog import args as index_args
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from pyquery import PyQuery


class TablePageCatalogTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.table_page.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                                             'type': 'String', 'vocabulary': '', 'options': []},
                                            {'id': 'col_b', 'label': 'Col B', 'description': '',
                                             'type': 'String', 'vocabulary': '', 'options': []},
                                            {'id': 'col_c', 'label': 'Col C', 'description': '',
                                             'type': 'String', 'vocabulary': '', 'options': []}
        ])
        self.tp_catalog = portal.tablepage_catalog
        self.storage = IDataStorage(portal.table_page)
        request.set('ACTUAL_URL', 'http://nohost/plone/table_page')

    def index_args(self, id):
        return index_args(doc_attr=id, lexicon_id='pg_lexicon', index_type='Okapi BM25 Rank')

    def test_search_form_not_shown1(self):
        portal = self.layer['portal']
        output = portal.table_page()
        self.assertFalse('id="searchTablePage"' in output)

    def test_search_form_not_shown2(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.assertFalse('id="searchTablePage"' in tp())

    def test_search_form_shown(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        output = tp()
        self.assertTrue('id="searchTablePage"' in output)

    def test_search_form_values_selector_shown(self):
        portal = self.layer['portal']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        self.tp_catalog.clearFindAndRebuild()
        output = tp()
        self.assertTrue('<select name="col_a:list"' in output)
        self.assertTrue('<option value="Foo Bar Baz">' in output)

    def test_search_form_postback1(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        self.tp_catalog.clearFindAndRebuild()
        request.form['col_a'] = 'Foo Bar Baz'
        output = tp()
        self.assertTrue('<select name="col_a:list"' in output)
        self.assertTrue('<option value="Foo Bar Baz" selected="selected">' in output)

    def test_search_form_postback2(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.tp_catalog.addIndex('col_a', 'ZCTextIndex', self.index_args('col_a'))
        self.tp_catalog.clearFindAndRebuild()
        request.form['col_a'] = 'Foo Bar Baz'
        output = tp()
        self.assertTrue('<input type="text" name="col_a" id="search_col_a" value="Foo Bar Baz" />' in output)

    def test_search_simple_filter(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.storage.add({'__creator__': 'user1', 'col_a': 'Qux Tux', '__uuid__': 'bbb'})
        self.tp_catalog.addIndex('col_a', 'FieldIndex')
        self.tp_catalog.clearFindAndRebuild()
        request.form['col_a'] = 'Foo Bar Baz'
        request.form['searchInTable'] = '1'
        pq = PyQuery(tp())
        table = pq('table.tablePage').text()
        self.assertTrue('Foo Bar Baz' in table)
        self.assertFalse('Qux Tux' in table)

    def test_search_text_filter(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': []}])
        self.storage.add({'__creator__': 'user1', 'col_a': 'Foo Bar Baz', '__uuid__': 'aaa'})
        self.storage.add({'__creator__': 'user1', 'col_a': 'Qux Bar Tux', '__uuid__': 'bbb'})
        self.storage.add({'__creator__': 'user1', 'col_a': 'XXX YYY', '__uuid__': 'ccc'})
        self.tp_catalog.addIndex('col_a', 'ZCTextIndex', self.index_args('col_a'))
        self.tp_catalog.clearFindAndRebuild()
        request.form['col_a'] = 'Bar'
        request.form['searchInTable'] = '1'
        pq = PyQuery(tp())
        table = pq('table.tablePage').text()
        self.assertTrue('Foo Bar Baz' in table)
        self.assertTrue('Qux Bar Tux' in table)
        self.assertFalse('XXX YYY' in table)

    def test_fulltext_search(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': ['SearchableText']},
                              {'id': 'col_b', 'label': '', 'description': '', 'additionalConfiguration': ['SearchableText']},
                              ])
        self.storage.add({'col_a': 'Foo Bar Baz', 'col_b': 'Foo Dom', '__uuid__': 'aaa'})
        self.storage.add({'col_a': 'Qux Bar Tux', 'col_b': 'FooFoo', '__uuid__': 'bbb'})
        self.tp_catalog.clearFindAndRebuild()
        request.form['SearchableText'] = 'Foo*'
        request.form['searchInTable'] = '1'
        pq = PyQuery(tp())
        table = pq('table.tablePage').text()
        self.assertTrue('Foo Dom' in table)
        self.assertTrue('FooFoo' in table)

    def test_fulltext_search_skip_col(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(searchConfig=[{'id': 'col_a', 'label': '', 'description': '', 'additionalConfiguration': ['SearchableText']},
                              {'id': 'col_b', 'label': '', 'description': '', 'additionalConfiguration': ['']},
                              ])
        self.storage.add({'col_a': 'Foo Bar', 'col_b': 'Baz Qux', '__uuid__': 'aaa'})
        self.storage.add({'col_a': 'Qux Tux', 'col_b': 'Bar', '__uuid__': 'bbb'})
        self.tp_catalog.clearFindAndRebuild()
        request.form['SearchableText'] = 'Bar*'
        request.form['searchInTable'] = '1'
        pq = PyQuery(tp())
        table = pq('table.tablePage').text()
        self.assertTrue('Foo Bar' in table)
        self.assertFalse('Qux Tux' in table)


class SearchWithBatchAndLabelTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.tp_catalog = portal.tablepage_catalog
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'foo_field', 'label': 'Foo field', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              ],
                batchSize=10)
        tp.edit(searchConfig=[{'id': 'foo_field', 'label': '', 'description': '',
                               'additionalConfiguration': ['SearchableText']}])
        self.tp = tp
        self.storage = IDataStorage(tp)
        self._addRows(35)
        self.tp_catalog.clearFindAndRebuild()

    def _addRows(self, nrows):
        for x in range(nrows):
            self.storage.add({'foo_field': 'aa%02d' % (x+1),
                              '__uuid__': '%05d' % (x+1)})

    def test_batching(self):
        tp = self.tp
        request = self.layer['request']
        request.form['searchInTable'] = '1'
        request.form['SearchableText'] = 'a*'
        self.storage.add({'foo_field': 'bbbbbbb', '__uuid__': '000'}, index=6)
        self.storage.add({'__label__': 'Section 1', '__uuid__': 'lll'}, index=3)
        self.tp_catalog.clearFindAndRebuild()
        output = tp()
        self.assertTrue('Section 1' in output)
        self.assertTrue('aa01' in output)
        self.assertTrue('aa09' in output)
        # this should be fixed someday
        self.assertFalse('aa10' in output)
        self.assertFalse('bbbbbbb' in output)

    def test_batching_page2(self):
        tp = self.tp
        request = self.layer['request']
        request.form['searchInTable'] = '1'
        request.form['SearchableText'] = 'a*'
        request.form['b_start'] = 10
        self.storage.add({'foo_field': 'bb', '__uuid__': '000'}, index=12)
        self.storage.add({'__label__': 'Section 1', '__uuid__': 'lll'}, index=3)
        self.tp_catalog.clearFindAndRebuild()
        output = tp()
        self.assertTrue('Section 1' in output)
        self.assertTrue('aa10' in output)
        self.assertFalse('bbbbbbb' in output)

    def test_batching_label_at_previous_page(self):
        tp = self.tp
        request = self.layer['request']
        request.form['searchInTable'] = '1'
        request.form['SearchableText'] = 'a*'
        request.form['b_start'] = 10
        self.storage.add({'foo_field': 'bb', '__uuid__': '000'}, index=11)
        self.storage.add({'__label__': 'Section 1', '__uuid__': 'lll'}, index=3)
        self.storage.add({'__label__': 'Section 2', '__uuid__': 'lll2'}, index=14)
        self.tp_catalog.clearFindAndRebuild()
        output = tp()
        self.assertTrue('Section 1' in output)
        self.assertTrue('Section 2' in output)
        self.assertTrue('aa10' in output)
        self.assertFalse('bbbbbbb' in output)


