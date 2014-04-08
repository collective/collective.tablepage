# -*- coding: utf-8 -*-

import unittest

from AccessControl import Unauthorized

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class SecurityTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        wtool = portal.portal_workflow
        login(portal, 'user1')
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []}])
        login(portal, TEST_USER_NAME)
        wtool.doActionFor(tp, 'publish')

    def test_base_access(self):
        """Member can access the tablepage but not the edit-table view"""
        portal = self.layer['portal']
        tp = portal.table_page
        login(portal, 'user0')
        self.assertTrue('Lorem Ipsum' in tp())
        self.assertRaises(Unauthorized, tp.restrictedTraverse, '@@tablepage-edit')
        # Contributor can do both
        login(portal, 'user1')
        self.assertTrue('Lorem Ipsum' in tp())
        self.assertTrue('Add new row' in tp.restrictedTraverse('@@tablepage-edit')())

    def test_add_row(self):
        """Every contributor (owner or not) can add new rows"""
        portal = self.layer['portal']
        tp = portal.table_page
        login(portal, 'user1')
        self.assertTrue('New row' in tp.restrictedTraverse('@@edit-record')())

    def test_modify_my_row(self):
        """user1 can modify it's own data"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1'})
        login(portal, 'user1')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['row-index'] = 0
        self.assertTrue('Edit row' in view())
        self.assertTrue('foo data from user1' in view())

    def test_modify_his_row(self):
        """user2 can't modify other user's data"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1'})
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['row-index'] = 0
        self.assertRaises(Unauthorized, view)

    def test_editor_modify_his_row(self):
        """user3 can modify other user's data"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1'})
        login(portal, 'user3')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['row-index'] = 0
        self.assertTrue('Edit row' in view())
        self.assertTrue('foo data from user1' in view())

    def test_move_my_row(self):
        """Owners normally can't move rows"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1'})
        storage.add({'__creator__': 'user1', 'col_a': 'some other futile data'})
        login(portal, 'user1')
        self.assertRaises(Unauthorized, tp.restrictedTraverse, '@@move-record')

    def test_editor_move_his_row(self):
        """Editor can move rows"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1', '__uuid__': 'aaa'})
        storage.add({'__creator__': 'user1', 'col_a': 'some other futile data', '__uuid__': 'bbb'})
        login(portal, 'user3')
        view = tp.restrictedTraverse('@@move-record')
        view.request.form['row-index'] = 0
        view.request.form['direction'] = 'down'
        view()
        self.assertEqual(storage[0].get('col_a'), 'some other futile data')

    def test_delete_my_row(self):
        """Owners can delete proper rows"""
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo data from user1'})
        login(portal, 'user1')
        view = tp.restrictedTraverse('@@delete-record')
        view.request.form['row-index'] = 0
        view()
        self.assertEqual(len(storage), 0)


class LabelAndGroupsSecurityTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        wtool = portal.portal_workflow
        login(portal, 'user1')
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        tp = portal.table_page
        tp.edit(textBefore='<p>Lorem Ipsum</p>',
                pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []}])
        login(portal, TEST_USER_NAME)
        wtool.doActionFor(tp, 'publish')
        storage = IDataStorage(tp)
        storage.add({'__creator__': 'user1', 'col_a': 'foo'})  # 0
        storage.add({'__creator__': 'user1', 'col_a': 'bar'})  # 1
        storage.add({'__label__': 'A label'})                  # 2
        storage.add({'__label__': 'B label'})                  # 3
        storage.add({'__creator__': 'user1', 'col_a': 'baz'})  # 4
        storage.add({'__creator__': 'user1', 'col_a': 'qux'})  # 5

    def test_add_end_of_group(self):
        # user can add data at the end of every group
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['addRow'] = '1'
        view.request.form['form.submitted'] = '1'
        # add before first label
        view.request.form['row-index'] = 1
        view.request.form['col_a'] = 'Added by me!'
        view()
        self.assertEqual(storage[2].get('col_a'), 'Added by me!')
        # add on first label
        view.request.form['row-index'] = 3
        view.request.form['col_a'] = 'Another added by me!'
        view()
        self.assertEqual(storage[4].get('col_a'), 'Another added by me!')
        # add at the end of document
        del view.request.form['row-index'] 
        view.request.form['col_a'] = 'Last added by me!'
        view()
        self.assertEqual(storage[-1].get('col_a'), 'Last added by me!')

    def test_add_end_of_group_cheat(self):
        # trying to cheat URL will not work, elements will be always at end of group
        portal = self.layer['portal']
        tp = portal.table_page
        storage = IDataStorage(tp)
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['row-index'] = 0
        view.request.form['addRow'] = '1'
        view.request.form['form.submitted'] = '1'
        view.request.form['col_a'] = 'Added by me!'
        view()
        self.assertEqual(storage[2].get('col_a'), 'Added by me!')
        view.request.form['row-index'] = 5
        view.request.form['col_a'] = 'Another added by me!'
        view()
        self.assertEqual(storage[-1].get('col_a'), 'Another added by me!')        

    def test_add_begin_of_group(self):
        # user can add data before the label or begin of group is insertType is 'prepend'
        portal = self.layer['portal']
        tp = portal.table_page
        tp.setInsertType('prepend')
        storage = IDataStorage(tp)
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['addRow'] = '1'
        view.request.form['form.submitted'] = '1'
        # add at the beginning of document
        view.request.form['col_a'] = 'Added by me!'
        view()
        self.assertEqual(storage[0].get('col_a'), 'Added by me!')
        # add on first label ("prepend" value will not change naything here)
        view.request.form['row-index'] = 3
        view.request.form['col_a'] = 'Another added by me!'
        view()
        self.assertEqual(storage[4].get('col_a'), 'Another added by me!')
        # add at the beginning of last group
        view.request.form['row-index'] = 5
        view.request.form['col_a'] = 'Last added by me!'
        view()
        self.assertEqual(storage[6].get('col_a'), 'Last added by me!')

    def test_add_begin_of_group_2(self):
        # When the first row is a label, always add after it
        portal = self.layer['portal']
        tp = portal.table_page
        tp.setInsertType('prepend')
        storage = IDataStorage(tp)
        storage.add({'__label__': 'New label'}, 0)                  # 0
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['addRow'] = '1'
        view.request.form['form.submitted'] = '1'
        view.request.form['row-index'] = 0
        view.request.form['col_a'] = 'Added by me!'
        view()
        self.assertEqual(storage[1].get('col_a'), 'Added by me!')

    def test_add_begin_of_group_cheat(self):
        # trying to cheat URL will not work, elements will be always at beginning of group
        portal = self.layer['portal']
        tp = portal.table_page
        tp.setInsertType('prepend')
        storage = IDataStorage(tp)
        login(portal, 'user2')
        view = tp.restrictedTraverse('@@edit-record')
        view.request.form['addRow'] = '1'
        view.request.form['form.submitted'] = '1'
        # add at the beginning of document
        view.request.form['col_a'] = 'Added by me!'
        view()
        self.assertEqual(storage[0].get('col_a'), 'Added by me!')
        # add on first label ("prepend" value will not change naything here)
        view.request.form['row-index'] = 3
        view.request.form['col_a'] = 'Another added by me!'
        view()
        self.assertEqual(storage[4].get('col_a'), 'Another added by me!')
        # add at the beginning of last group
        view.request.form['row-index'] = 5
        view.request.form['col_a'] = 'Last added by me!'
        view()
        self.assertEqual(storage[6].get('col_a'), 'Last added by me!')
