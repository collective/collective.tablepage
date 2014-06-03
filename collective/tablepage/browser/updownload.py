# -*- coding: utf-8 -*-

import csv
import uuid
from Products.Five.browser import BrowserView
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from collective.tablepage import config
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import IColumnDataRetriever
from collective.tablepage.interfaces import IColumnField
from collective.tablepage.interfaces import IFieldValidator
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage import logger
from zope.component import getAdapter
from zope.component import getAdapters
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

    def _getRetrieveValidators(self, col_type):
        field = getMultiAdapter((self.context, self.request),
                                IColumnField, name=col_type)
        validators = getAdapters((field, ),
                                 IFieldValidator)
        return [(x[0], x[1]) for x in validators]

    def __call__(self):
        # PLEASE refactorgin this mess
        request = self.request
        context = self.context
        file = request.form.get('csv')
        check_duplicate = request.form.get('look_for_duplicate')
        tp_catalog = getToolByName(context, config.CATALOG_ID)
        if file and file.filename:
            try:
                dialect = csv.Sniffer().sniff(file.read(1024), delimiters=";,")
                if not dialect.delimiter:
                    # some stupid Python 2.4 CSV bug may happens
                    raise csv.Error
            except csv.Error:
                dialect = 'excel'
            file.seek(0)
            counter = 0
            storage = IDataStorage(context)
            member = getMultiAdapter((context, request), name=u'plone_portal_state').member()
            reader = csv.reader(file, dialect)

            configuration = self.context.getPageColumns()
            valid_headers = [c['id'] for c in configuration]
            valid_retrievers = [self._getRetrieverAdapter(c['type']) for c in configuration]
            validators = [self._getRetrieveValidators(c['type']) for c in configuration]
 
            headers = []
            first = True
            putils = getToolByName(context, 'plone_utils')
            for line, row in enumerate(reader):
                logger.info("Importing line %04d" % line)
                if first:
                    headers = [h.strip() for h in row if h.strip()]
                    if configuration:
                        # CSV row is accessed by index
                        headers = [(h, headers.index(h)) for h in headers if h in valid_headers]
                    else:
                        # No configuration. Let's guess a configuration using CSV headers
                        self.context.setPageColumns([{'id' : h,
                                                      'label' : h,
                                                      'description' : '',
                                                      'type' : 'String',
                                                      'vocabulary' : '',
                                                      'options' : [],
                                                      } for h in headers])
                        headers = [(h, headers.index(h)) for h in headers]
                        configuration = self.context.getPageColumns()
                        valid_retrievers = [self._getRetrieverAdapter(c['type']) for c in configuration]
                        validators = [self._getRetrieveValidators(c['type']) for c in configuration]
                    first = False
                    continue

                tobe_saved = {}
                skip_row = False

                if len(row)<len(headers):
                    putils.addPortalMessage(_('error_row_count_dont_match',
                                              default=u"Skipping line $line. Found $lrow columns instead of $lheaders",
                                              mapping={'line': line+1,
                                                       'lrow': len(row),
                                                       'lheaders': len(headers)}),
                                            type="error")
                    continue


                for header, hindex in headers:
                    skip_cell = False
                    if request.form.get('validate'):
                        required_field_validation_failed = False
                        for vname, v in validators[hindex]:
                            msg = v.validate(configuration[hindex], data=row[hindex])
                            if msg:
                                if vname==u'required':
                                    putils.addPortalMessage(_('warn_invalid_row',
                                                              default=u"Line $line can't be imported due to missing "
                                                                      u"required data",
                                                              mapping={'line': line+1}),
                                                            type="warning")
                                    required_field_validation_failed = True
                                    break
                                putils.addPortalMessage(_('warn_invalid_cell',
                                                          default=u"Line $line, cell $cell: can't import data "
                                                                  u"due to failed validator check",
                                                          mapping={'line': line+1, 'cell': hindex}),
                                                        type="warning")
                                skip_cell = True
                                break

                        if required_field_validation_failed:
                            skip_row = True
                            break

                    # do not spend time to save data if this will be discarded
                    if not skip_row and not skip_cell:
                        try:
                            tobe_saved[header] = valid_retrievers[hindex].data_to_storage(row[hindex])
                        except NotImplementedError:
                            # column is not implementing CSV data load
                            continue

                if not skip_row and tobe_saved:
                    if check_duplicate and self._checkDuplicateRow(tobe_saved, storage):
                        putils.addPortalMessage(_('warn_duplicate',
                                                  default=u"Line ${line_number} not added because duplicated "
                                                          u"data has been found",
                                                  mapping={'line_number': line+1}),
                                                type="warning")
                        continue
                    tobe_saved['__creator__'] = member.getId()
                    tobe_saved['__uuid__'] = str(uuid.uuid4())
                    counter += 1
                    storage.add(tobe_saved)
                    tp_catalog.catalog_row(context, tobe_saved)
            msg = _('count_rows_added',
                    default=u'${count} rows added',
                    mapping={'count': counter})
            putils.addPortalMessage(msg)
            self._addNewVersion(msg)
            #return request.response.redirect('%s/edit-table' % context.absolute_url())
        return self.index()

    def _addNewVersion(self, comment=''):
        """Content must be updated, so the history machinery will save a new version"""
        context = self.context
        context.reindexObject()
        if VERSIONING_SUPPORT and isObjectChanged(context) and isObjectVersioned(context):
            maybeSaveVersion(context, comment=comment)

    def _checkDuplicateRow(self, new_line, storage):
        """Iterate onto the storage, returns True if there's at least a row with the same data of the new row"""
        total_cols = len(self.context.getPageColumns())
        for row in storage:
            found_entries = 0
            for k,v in new_line.items():
                if row.get(k)==v:
                    found_entries += 1
            if found_entries==total_cols:
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
        table_configuration = self.context.getPageColumns()
        for conf in table_configuration:
            column = {}
            column['display_header'] = for_editor and conf.get('id') or (conf.get('label') or conf.get('id'))
            column['header_code'] = conf.get('id')
            column['configuration'] = conf
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
        csvparams = {'quoting' :csv.QUOTE_ALL,
                     'delimiter': self.request.form.get('delimiter', ',')
                     }
        writer = csv.writer(file, **csvparams)
        writer.writerow([h['display_header'] for h in columns])

        for row_index, data in enumerate(storage):
            row = []
            if data.get('__label__'):
                continue
            for header in columns:
                adapter = header['adapter']
                adapter.configuration = header['configuration']
                try:
                    col_val = adapter.data_for_display(data.get(header['header_code']),
                                                       backend=for_editor, row_index=row_index) or ''
                except NotImplementedError:
                    # Column will not export anything
                    row.append('')
                    continue
                if not isinstance(col_val, basestring):
                    # a sequence, probably
                    col_val = '\n'.join(col_val)
                row.append(col_val.strip())
            writer.writerow(row)
        response = self.request.response
        response.setHeader('Content-Type','text/csv')
        response.addHeader('Content-Disposition', 'attachment; filename=%s.csv' % self.context.getId())
        response.write(file.getvalue())
