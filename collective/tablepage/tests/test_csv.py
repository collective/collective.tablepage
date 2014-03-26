# -*- coding: utf-8 -*-

import unittest
from StringIO import StringIO
from zope.component import getMultiAdapter

from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


def get_csv_content(view, skipHeaders=False):
    """Return CSV content as a grid (list of lists)"""
    stdout = StringIO()
    native_stdout = view.request.response.stdout
    view.request.response.stdout = stdout
    view()
    data = stdout.getvalue()
    view.request.response.stdout = native_stdout
    return "\n".join(data.splitlines()[(not skipHeaders and 6 or 0):])


class CSVExportTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.invokeFactory(type_name='File', id='file1', title="Attachment 1")
        portal.invokeFactory(type_name='File', id='file2', title="Attachment 2")
        portal.invokeFactory(type_name='Document', id='document1', title="Page 1")
        self.storage = IDataStorage(portal.table_page)

    def test_emtpy_csv(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': ''},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A","Col B"')
        request.form['target'] = 'editor'
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view, skipHeaders=True)
        self.assertEqual(csv, '"col_a","col_b"')

    def test_labels_ignored(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': 'foo', 'col_b': 'bar'})
        self.storage.add({'__label__': 'A label'})
        self.storage.add({'__creator__': 'user1', 'col_a': 'baz', 'col_b': 'qux'})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A","Col B"\n'
                              '"foo","bar"\n'
                              '"baz","qux"')

    def test_string_field(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': 'foo bar'})
        self.storage.add({'__creator__': 'user1', 'col_a': ' baz  qux'})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"foo bar"\n'
                              '"baz  qux"')

    def test_text_field(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Text', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': 'foo\n\nbar\t\t '})
        self.storage.add({'__creator__': 'user1', 'col_a': ' \nbaz \nqux'})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"foo\n\nbar"\n'
                              '"baz \nqux"')

    def test_file_field(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': portal.file1.UID()})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"%s/file1"' % portal.absolute_url())
        request.form['target'] = 'editor'
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view, skipHeaders=True)
        self.assertEqual(csv, '"col_a"\n"%s"' % portal.file1.UID())

    def test_multiple_file_field(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': "%s\n%s" % (portal.file1.UID(),
                                                                       portal.file2.UID(),)})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"%s/file1\n'
                              '%s/file2"' % (portal.absolute_url(), portal.absolute_url()))
        request.form['target'] = 'editor'
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view, skipHeaders=True)
        self.assertEqual(csv, '"col_a"\n"%s\n%s"' % (portal.file1.UID(),
                                                   portal.file2.UID(),))

    def test_link_field_simple_url(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': "http://plone.org/"})
        self.storage.add({'__creator__': 'user1', 'col_a': "http://planet.plone.org/"})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"http://plone.org/"\n'
                              '"http://planet.plone.org/"')

    def test_link_field_internal(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        self.storage.add({'__creator__': 'user1', 'col_a': portal.document1.UID()})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A"\n'
                              '"%s/document1"' % portal.absolute_url())
        request.form['target'] = 'editor'
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view, skipHeaders=True)
        self.assertEqual(csv, '"col_a"\n"%s"' % portal.document1.UID())

    def test_computed_field(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                             {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'Computed', 'vocabulary': 'row/col_a\ncache:1', 'options': []},
                              ])
        self.storage.add({'__creator__': 'user1', 'col_a': 'lorem ipsum'})
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view)
        self.assertEqual(csv, '"Col A","Col B"\n'
                              '"lorem ipsum","lorem ipsum"')
        request.form['target']='editor'
        view = getMultiAdapter((tp, request), name=u"download-table")
        csv = get_csv_content(view, skipHeaders=True)
        self.assertEqual(csv, '"col_a","col_b"\n'
                              '"lorem ipsum",""')


class CSVImportTestCase(unittest.TestCase):

    layer = TABLE_PAGE_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='TablePage', id='table_page', title="The Table Document")
        portal.invokeFactory(type_name='File', id='file1', title="Attachment 1")
        portal.invokeFactory(type_name='File', id='file2', title="Attachment 2")
        portal.invokeFactory(type_name='Document', id='document1', title="Page 1")
        portal.invokeFactory(type_name='Folder', id='folder', title="Folder")
        portal.folder.invokeFactory(type_name='File', id='file3', title="Attachment 3")
        portal.folder.invokeFactory(type_name='Document', id='document2', title="Page 2")
        self.storage = IDataStorage(portal.table_page)

    def file_with_data(self, data):
        file = StringIO()
        file.filename = 'test.csv'
        file.write(data)
        file.seek(0)
        return file

    def test_ignore_whitespaces(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        file = self.file_with_data("col_a,col_b \n"
                                   "foo,  bar")
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], 'foo')
        self.assertEqual(self.storage[0]['col_b'], 'bar')

    def test_ignore_unknow_cols(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_c', 'label': 'Col C', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        file = self.file_with_data("col_a,col_a1,col_b\n"
                                   "foo,bar,baz")
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], 'foo')
        self.assertEqual(self.storage[0].get('col_a1'), None)
        self.assertEqual(self.storage[0].get('col_b'), 'baz')

    def test_rowswith_few_cols_unknow_cols(self):
        # Skipping line 2. Found 3 columns instead of 2
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_c', 'label': 'Col C', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        file = self.file_with_data("col_a,col_b,col_c\n"
                                   "foo,baz\n"
                                   "lorem,ipsum,dolor")
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        output = view()
        self.assertTrue('Skipping line 2. Found 2 columns instead of 3' in output)
        self.assertEqual(len(self.storage), 1)
        self.assertEqual(self.storage[0]['col_a'], 'lorem')

    def test_text_field(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Text', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"  foo bar\n \nbaz\n"')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], 'foo bar\n \nbaz')

    # ******* FILE *******
    def test_file_field_uid(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n' + portal.file1.UID())
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], portal.file1.UID())

    def test_file_field_unknow_uid(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\nzzzZZZzzzZZZzzz')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], None)

    def test_file_field_url(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '%s/file1\n'
                                   '%s/file3' % (portal.absolute_url(),
                                                 portal.folder.absolute_url()))
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], portal.file1.UID())
        self.assertEqual(self.storage[1]['col_a'], portal.folder.file3.UID())

    def test_file_field_path(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'File', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   'file1\n'
                                   '/folder/file3')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], portal.file1.UID())
        self.assertEqual(self.storage[1]['col_a'], portal.folder.file3.UID())

    # ******* FILES *******
    def test_files_field_uids(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"%s\n%s"' % (portal.file1.UID(),
                                                 portal.file2.UID(),))
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], "%s\n%s" % (portal.file1.UID(),
                                                               portal.file2.UID(),))

    def test_files_field_unknow_uids(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"zzzZZZzzzZZZzzz\nbbbbbbb"')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], None)

    def test_files_field_good_and_bad_uids(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"%s\n\nbbbbbbb\n%s"' % (portal.file1.UID(),
                                                          portal.file2.UID(),))
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], "%s\n%s" % (portal.file1.UID(),
                                                               portal.file2.UID()))

    def test_files_field_URLs(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"%s\n%s"' % (portal.file1.absolute_url(),
                                                 portal.file2.absolute_url(),))
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], "%s\n%s" % (portal.file1.UID(),
                                                               portal.file2.UID()))

    def test_files_field_paths(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Files', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '"file1\n/file2"')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], "%s\n%s" % (portal.file1.UID(),
                                                               portal.file2.UID()))

    # ******* LINK *******
    def test_link_field_uuid(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n%s' % portal.document1.UID())
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], portal.document1.UID())

    def test_link_field_unknow_uid(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\nzzzZZZzzzZZZzzz')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], None)

    def test_link_field_internal_URL(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   '%s\n'
                                   '%s' % (portal.document1.absolute_url(),
                                           portal.folder.document2.absolute_url()))
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], portal.document1.UID())
        self.assertEqual(self.storage[1]['col_a'], portal.folder.document2.UID())

    def test_link_field_URL(self):
        portal = self.layer['portal']
        tp = portal.table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'Link', 'vocabulary': '', 'options': []},])
        file = self.file_with_data('col_a\n'
                                   'http://plone.org/')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], 'http://plone.org/')

    def test_checkDuplicateRow(self):
        portal = self.layer['portal']
        request = self.layer['request']
        tp = portal.table_page
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                              {'id': 'col_c', 'label': 'Col C', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},])
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        self.storage.add({'col_a': 'aaa', 'col_b': 'bbb', 'col_c': 'ccc'})
        # totally new line does not match
        self.assertEqual(view._checkDuplicateRow({'col_a': 'foo', 'col_b': 'foo', 'col_c': 'foo', },
                                                 self.storage), False)
        # only a single difference is enough for being a new row
        self.assertEqual(view._checkDuplicateRow({'col_a': 'aaa', 'col_b': 'bbb', 'col_c': 'foo', },
                                                 self.storage), False)
        # empty data is not ignored
        self.assertEqual(view._checkDuplicateRow({'col_a': 'aaa', 'col_b': 'bbb', },
                                                 self.storage), False)
        # testing equal row
        self.assertEqual(view._checkDuplicateRow({'col_a': 'aaa', 'col_b': 'bbb', 'col_c': 'ccc', },
                                                 self.storage), True)
        self.storage.add({'col_a': 'aaa', 'col_b': 'bbb', 'col_c': ''})
        self.assertEqual(view._checkDuplicateRow({'col_a': 'aaa', 'col_b': 'bbb', 'col_c': ''},
                                                 self.storage), True)

    def test_computed_field(self):
        tp = self.layer['portal'].table_page
        request = self.layer['request']
        tp.edit(pageColumns=[{'id': 'col_a', 'label': 'Col A', 'description': '',
                              'type': 'String', 'vocabulary': '', 'options': []},
                             {'id': 'col_b', 'label': 'Col B', 'description': '',
                              'type': 'Computed', 'vocabulary': 'row/col_a\ncache:1', 'options': []},
                              ])
        file = self.file_with_data('col_a,col_b\n'
                                   '"foo bar","not used"')
        request.form['csv'] = file
        view = getMultiAdapter((tp, request), name=u"upload-rows")
        view()
        self.assertEqual(self.storage[0]['col_a'], 'foo bar')
        self.assertEqual(self.storage[0].get('col_b'), None)
