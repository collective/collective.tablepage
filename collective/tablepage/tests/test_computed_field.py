# -*- coding: utf-8 -*-

import unittest

from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class ComputedFieldTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.invokeFactory(type_name='Document', id='document', title="A document to reference")
        portal.invokeFactory(type_name='File', id='file1', title="One file")
        portal.invokeFactory(type_name='File', id='file2', title="Another file")
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'column_file', 'label': 'A file', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},
                             {'id': 'column_files', 'label': 'Some files', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},
                             {'id': 'column_link', 'label': 'Link', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},
                             {'id': 'simple_column', 'label': 'Link', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                             {'id': 'computed', 'label': 'Computed', 'description': '',
                              'type': 'Computed', 'vocabulary': '', 'options': []},
                              ])
        self.tp = tp

    def _getField(self):
        request = self.layer['request']
        field = getMultiAdapter((self.tp, request),
                                IColumnField, name=u'Computed')
        field.configuration = self.tp.getPageColumns()[-1]
        return field

    def test_computed_simple_row_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'simple_column': 'Lorem ipsum'})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = 'row/simple_column'
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'Lorem ipsum')

    def test_computed_general_tal_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'simple_column': 'Lorem ipsum'})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = 'portal/title'
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'Plone site')

    def test_index_var_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'simple_column': 'Lorem ipsum'})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = "python:index * 2"
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), '0')
        storage.add({'simple_column': 'dolor sit amet'})
        field = self._getField()
        self.assertEquals(field.render_view('foo', 1).strip(), '2')

    def test_rows_var_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'simple_column': 'Lorem ipsum'})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = "python:rows.get(0)['simple_column']"
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'Lorem ipsum')
        storage.add({'simple_column': 'dolor sit amet'})
        field = self._getField()
        self.assertEquals(field.render_view('foo', 1).strip(), 'Lorem ipsum')

    def test_computed_file_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'column_file': portal.file1.UID()})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = 'row/column_file/Title'
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'One file')

    def test_computed_multiple_files_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'column_files': "%s\n%s" % (portal.file1.UID(), portal.file2.UID())})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = "python:row['column_files'][1].Title()"
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'Another file')

    def test_computed_link_access(self):
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'column_link': portal.document.UID()})
        storage.add({'column_link': 'http://plone.org/'})
        configuration = tp.getPageColumns()
        configuration[-1]['vocabulary'] = "row/column_link/Title|row/column_link"
        field = self._getField()
        self.assertEquals(field.render_view('foo', 0).strip(), 'A document to reference')
        self.assertEquals(field.render_view('foo', 1).strip(), 'http://plone.org/')

