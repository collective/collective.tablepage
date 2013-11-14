# -*- coding: utf-8 -*-

import csv
from Products.Five.browser import BrowserView
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage import tablepageMessageFactory as _
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

try:
    from Products.CMFEditions.utilities import isObjectChanged
    from Products.CMFEditions.utilities import maybeSaveVersion
    from Products.CMFEditions.utilities import isObjectVersioned
    VERSIONING_SUPPORT = True
except ImportError:
    # No versioning support for Plone 3.3 version of CMFEditions
    VERSIONING_SUPPORT = False


class UploadDataView(BrowserView):
    """Massive upload of rows using CSV"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.set('disable_border', True)

    def _getRetrieverAdapter(self, col_type):
           
        try:
            retriever = getAdapter(self.context,
                                   IColumnDataRetriever,
                                   name=col_type)
        except ComponentLookupError:
            retriever = IColumnDataRetriever(self.context)
        return retriever

    def __call__(self):
        request = self.request
        context = self.context
        file = request.form.get('csv')
        check_duplicate = request.form.get('look_for_duplicate')
        if file and file.filename:
            counter = 0
            storage = IDataStorage(context)
            member = getMultiAdapter((context, request), name=u'plone_portal_state').member()
            reader = csv.reader(file)

            configuration = self.context.getPageColumns()
            valid_headers = [c['id'] for c in configuration]
            valid_retrievers = [self._getRetrieverAdapter(c['type']) for c in configuration]
 
            headers = []
            first = True
            putils = getToolByName(context, 'plone_utils')
            for line, row in enumerate(reader):
                if first:
                    headers = [h.strip() for h in row if h.strip()]
                    # CSV row is accessed by index
                    headers = [(h, headers.index(h)) for h in headers if h in valid_headers]
                    first = False
                    continue
                tobe_saved = {}
                for header, hindex in headers:
                    tobe_saved[header] = valid_retrievers[hindex].data_to_storage(row[hindex])
                if tobe_saved:
                    if check_duplicate and self._checkDuplicateRow(tobe_saved, storage):
                        putils.addPortalMessage(_('warn_duplicate',
                                                  default=u"Line ${line_number} not added because duplicated "
                                                          u"data has been found",
                                                  mapping={'line_number': line+1}),
                                                type="warning")
                        continue
                    tobe_saved['__creator__'] = member.getId()
                    counter += 1
                    storage.add(tobe_saved)
            msg = _('count_rows_added',
                    default=u'${count} rows added',
                    mapping={'count': counter})
            putils.addPortalMessage(msg)
            self._addNewVersion(msg)
            return request.response.redirect('%s/edit-table' % context.absolute_url())
        return self.index()

    def _addNewVersion(self, comment=''):
        """Content must be updated, so the history machinery will save a new version"""
        context = self.context
        context.reindexObject()
        if VERSIONING_SUPPORT and isObjectChanged(context) and isObjectVersioned(context):
            maybeSaveVersion(context, comment=comment)

    def _checkDuplicateRow(self, new_line, storage):
        """Iterate onto the storage, returns True if there's at least a row with the sae data of the new row"""
        for row in storage:
            for k,v in new_line.items():
                if row.get(k)==v:
                    return True
        return False

    @property
    def defined_cols(self):
        return ['"%s"' % c['id'] for c in self.context.getPageColumns()]


class DownloadDataView(BrowserView):
    """Download all table data in CSV format
    CSV will contain an header row. Headers will be columns ids or labels.
    """
    
    def __call__(self):
        target = self.request.form.get('target')
        for_editor = target == 'editor' or False
        columns = []
        for conf in self.context.getPageColumns():
            column = {}
            column['display_header'] = for_editor and conf.get('id') or (conf.get('label') or conf.get('id'))
            column['header_code'] = conf.get('id')
            try:
                retriever = getAdapter(self.context,
                                       IColumnDataRetriever,
                                       name=conf['type'])
            except ComponentLookupError:
                retriever = IColumnDataRetriever(self.context)
            column['adapter'] = retriever
            columns.append(column)
        storage = IDataStorage(self.context)
        file = StringIO()
        writer = csv.writer(file)
        writer.writerow([h['display_header'] for h in columns])
        for data in storage:
            row = []
            if data.get('__label__'):
                continue
            for header in columns:
                adapter = header['adapter']
                col_val = adapter.data_for_display(data.get(header['header_code']), backend=for_editor) or ''
                if not isinstance(col_val, basestring):
                    # a sequence, probably
                    col_val = '\n'.join(col_val)
                row.append(col_val.strip())
            writer.writerow(row)
        response = self.request.response
        response.setHeader('Content-Type','text/csv')
        response.addHeader('Content-Disposition', 'attachment; filename=%s.csv' % self.context.getId())
        response.write(file.getvalue())
