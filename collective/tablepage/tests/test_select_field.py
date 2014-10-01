# -*- coding: utf-8 -*-

import unittest

from zope.component import getMultiAdapter
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class SelectFieldTestCase(unittest.TestCase):
    
    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'foo', 'label': 'Select one', 'description': '',
                              'type': 'Select', 'vocabulary': 'Lorem\nIpsum\ndolor\nsit\n amet',
                              'options': []}
        ])
        self.storage = IDataStorage(tp)

    def test_access_creation_form(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        view = getMultiAdapter((tp, request), name='edit-record')
        self.assertTrue('<select id="foo" name="foo">' in view())

    def test_access_edit_form(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        self.storage.add({'__creator__': 'foo', 'foo': 'Ipsum'})
        request.form['row-index'] = 0
        view = getMultiAdapter((tp, request), name='edit-record')
        output = view()
        self.assertTrue('<select id="foo" name="foo">' in output)
        self.assertTrue('<option value="Ipsum" selected="selected">' in output)

    def test_access_computed_vocabulary(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'col1', 'label': 'Select one', 'description': '',
                              'type': 'Select', 'vocabulary': 'vocabulary:context/Subject\n'
                                                              'alpha\n'
                                                              'vocabulary:python:["item-1", "item-2", "item-3"]\n'
                                                              'omega\n',
                              'options': []}
        ])
        tp.setSubject(['foo', 'bar', 'baz'])
        self.storage.add({'__creator__': 'user1', 'col1': 'bar', '__uuid__': 'aaa'})
        request.form['row-index'] = 0
        view = getMultiAdapter((tp, request), name='edit-record')
        output = view()
        self.assertTrue('<option value="bar" selected="selected">bar</option>' in output)
        self.assertTrue('<option value="alpha">alpha</option>' in output)
        self.assertTrue('<option value="item-1">item-1</option>' in output)
        self.assertTrue('<option value="item-2">item-2</option>' in output)        
        self.assertTrue('<option value="omega">omega</option>' in output)

    def test_edit_computed_vocabulary(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'col1', 'label': 'Select one', 'description': '',
                              'type': 'Select', 'vocabulary': 'vocabulary:context/Subject\n'
                                                              'alpha\n'
                                                              'vocabulary:python:["item-1", "item-2", "item-3"]'
                                                              'omega\n',
                              'options': []}
        ])
        tp.setSubject(['foo', 'bar', 'baz'])
        self.storage.add({'__creator__': 'user1', 'col1': 'bar', '__uuid__': 'aaa'})
        request.form['row-index'] = 0
        request.form['form.submitted'] = '1'
        request.form['col1'] = 'baz'
        view = getMultiAdapter((tp, request), name='edit-record')
        view()
        self.assertEqual(self.storage[0]['col1'], 'baz')
