# -*- coding: utf-8 -*-

import unittest
from DateTime import DateTime
from zope.component import getMultiAdapter
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class CachingTestCase(unittest.TestCase):
    
    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'the_text_data', 'label': 'A text', 'description': '',
                              'type': 'Text', 'vocabulary': '', 'options': []}
        ])
        self.storage = IDataStorage(tp)

    def test_cache_miss(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.form['form.submitted'] = '1'
        request.form['the_text_data'] = 'Lorem ipsum'
        tp = portal.table_page
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        self.assertEqual(self.storage[0]['__cache__']['the_text_data']['data'], '<p>Lorem ipsum</p>\n')
        self.assertTrue(self.storage[0]['__cache__']['the_text_data']['timestamp'] < DateTime().millis())

    def test_cache_hit(self):
        portal = self.layer['portal']
        tomorrow = DateTime() + 1
        self.storage.add({'__creator__': 'foo', 'the_text_data': 'foo bar baz',
                          '__cache__': {'the_text_data': {'data': 'In cache we believe',
                                                          'timestamp': tomorrow.millis()}}})
        output = portal.table_page()
        self.assertTrue('In cache we believe' in output)
        self.assertFalse('foo bar baz' in output)

    def test_cache_miss_timestamp_expired(self):
        portal = self.layer['portal']
        self.storage.add({'__creator__': 'foo', 'the_text_data': 'foo bar baz',
                          '__cache__': {'the_text_data': {'data': 'In cache we believe',
                                                          'timestamp': 0}}})
        output = portal.table_page()
        self.assertFalse('In cache we believe' in output)
        self.assertTrue('<p>foo bar baz</p>' in output)
