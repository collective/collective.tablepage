# -*- coding: utf-8 -*-

import re

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.DataGridField.Column import Column
from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.TinyMCE.interfaces.utility import ITinyMCE
from collective.datagridcolumns.MultiSelectColumn import MultiSelectColumn
from collective.datagridcolumns.SelectColumn import SelectColumn
from collective.datagridcolumns.TextAreaColumn import TextAreaColumn
from collective.tablepage import config
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IDataStorage
from collective.tablepage.interfaces import ITablePage
from zope.component import queryUtility
from zope.interface import implements

try:
    from archetypes.referencebrowserwidget import ReferenceBrowserWidget
except ImportError:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget


TablePageSchema = ATDocumentSchema.copy() + atapi.Schema((

    atapi.TextField('textBefore',
              required=False,
              searchable=True,
              storage=atapi.AnnotationStorage(migrate=True),
              validators=('isTidyHtmlWithCleanup',),
              default_output_type='text/x-html-safe',
              widget=atapi.RichWidget(
                        label=_(u'label_text_before', default=u'Text before the table'),
                        visible={'view': 'invisible', 'edit': 'visible'},
                        rows=25,
                        allow_file_upload=zconf.ATDocument.allow_document_upload),
    ),

    DataGridField('pageColumns',
        required=True,
        storage=atapi.AnnotationStorage(),
        columns=("id", "label", "description", "type", "vocabulary", "options"),
        widget=DataGridWidget(
            label=_(u"Columns"),
            description=_('help_pageColumns',
                          default=u"Definition of rows inside the table"),
            visible={'view': 'invisible', 'edit': 'visible'},
            helper_js= ('datagridwidget.js', 'datagridwidget_patches.js', 'datagridmultiselect.js'),
            columns={
                 'id' : Column(_(u"Column id"), required=True),
                 'label' : Column(_(u"Column label"), required=True),
                 'description' : TextAreaColumn(_(u"Column description")),
                 'type' : SelectColumn(_(u"Type of data"),
                                       vocabulary_factory="collective.tablepage.vocabulary.column_types",
                                       required=True,
                                       default="String"),
                 'vocabulary' : TextAreaColumn(_(u"Column configuration"),
                                               col_description=_("vocabulary_column_description",
                                                                   default=u"Some columns types will need this.\n"
                                                                           u"For \"Select\" type: used for defining the "
                                                                           u"vocabulary (one item on per row).\n"
                                                                           u"For \"Computed\" type: write there the TALES expression.")),
                 'options' : MultiSelectColumn(_(u"Additional features"),
                                               col_description=_("options_column_description",
                                                                   default=u"Other options you can activate on the column"),
                                               vocabulary_factory="collective.tablepage.vocabulary.row_options"),
            },
        ),
    ),

    atapi.StringField('tableCaption',
              required=False,
              searchable=False,
              widget=atapi.StringWidget(
                        label=_(u'Table caption'),
                        description=_('help_table_caption',
                                      default=u'Optional summary of table contents'),
                        size=50,
                        visible={'view': 'invisible', 'edit': 'visible'},
            ),
    ),

    atapi.LinesField('cssClasses',
              required=False,
              searchable=False,
              vocabulary='getCSSClassesVocabulary',
              default=["listing"],
              widget=atapi.MultiSelectionWidget(
                        label=_(u'CSS classes'),
                        description=_(u'CSS classes to be applied to the table.\n'
                                      u'This list is taken from available TinyMCE style for tables.'),
                        format="checkbox",
                        visible={'view': 'invisible', 'edit': 'visible'},
                        condition="object/getCSSClassesVocabulary",
            ),
    ),

    atapi.ComputedField('text',
        expression="object/getText",
        searchable=True,        
        widget=atapi.ComputedWidget(
            label=ATDocumentSchema['text'].widget.label,
            description=ATDocumentSchema['text'].widget.description,
        )
    ),

    atapi.TextField('textAfter',
              required=False,
              searchable=True,
              storage=atapi.AnnotationStorage(migrate=True),
              validators=('isTidyHtmlWithCleanup',),
              default_output_type='text/x-html-safe',
              widget=atapi.RichWidget(
                        label=_(u'label_text_after', default=u'Text after the table'),
                        visible={'view': 'invisible', 'edit': 'visible'},
                        rows=25,
                        allow_file_upload=zconf.ATDocument.allow_document_upload),
    ),

    atapi.ReferenceField('attachmentStorage',
            allowed_types=('Folder',),
            relationship="tablepage_storage",
            widget=ReferenceBrowserWidget(label=_(u"Attachment storage"),
                                          description=_('attachmentStorage_help',
                                                        default=u"Select the folder where users will be able to store attachments for "
                                                                u"attachment-like columns (if any).\n"
                                                                u"Users must be able to add new contents on that folder; if not, they "
                                                                u"will be only able to select existings items.\n"
                                                                u"If not provided, the folder containing this document will be used."),
                                          force_close_on_insert=True,
                                          visible={'view': 'invisible', 'edit': 'visible'},
                                          ),
    ),

    atapi.BooleanField('downloadEnabled',
              required=False,
              searchable=False,
              schemata="settings",
              widget=atapi.BooleanWidget(
                        label=_(u'Show download link for data'),
                        description=_('help_download_enabled',
                                      default=u'Display a download link for data inside the table in CSV format'),
            ),
    ),

    atapi.StringField('showHeaders',
              searchable=False,
              schemata="settings",
              default="always",
              vocabulary="showHeadersVocabulary",
              enforceVocabulary=True,
              widget=atapi.SelectionWidget(
                        label=_(u'Show headers'),
                        description=_(u'Show table headers when...'),
            ),
    ),

    atapi.StringField('insertType',
              searchable=False,
              schemata="settings",
              default="append",
              vocabulary="insertTypeVocabulary",
              enforceVocabulary=True,
              widget=atapi.SelectionWidget(
                        label=_(u'Criteria for adding new rows'),
                        description=_('help_insertType',
                                      default=u'Criteria of inserting new row.\n'
                                              u'Choose if add row at the end of group (append) '
                                              u'or before group (prepend).'),
            ),
    ),

    atapi.IntegerField('batchSize',
              searchable=False,
              schemata="settings",
              default=100,
              required=True,
              widget=atapi.IntegerWidget(
                        label=_(u'Max number of rows'),
                        description=_('help_batchSize',
                                      default=u'Insert the maximum number of rows to be displayed '
                                              u'in a single page.\n'
                                              u'When this limit is reached a batching navigation section '
                                              u'will be displayed.\n'
                                              u'Use 0 to disable batching (NOT suggested on very large tables or '
                                              u'extremly complex column types).'),
              ),
    ),

    # FOO FIELD!!!! Only needed to being able to use the ATReferenceBrowserWidget... :(
    atapi.StringField('link_internal',
            widget=ReferenceBrowserWidget(
                    label=u"Internal link dump field",
                    visible={'view': 'invisible', 'edit': 'invisible'},
                    force_close_on_insert=True,
                    startup_directory_method="this_directory",
            ),
    ),

    DataGridField('searchConfig',
        required=False,
        storage=atapi.AnnotationStorage(),
        schemata="search",
        columns=("id", "label", "description", "additionalConfiguration"),
        write_permission=config.MANAGE_SEARCH_PERMISSION,
        widget=DataGridWidget(
            label=_(u"Search configuration"),
            description=_('help_searchConfig',
                          default=u"Provide configuration for the search in table.\n"
                                  u"Please note that this section will not load live data from the \"Columns\" field. "
                                  u"If you changed something in the columns configuration during this edit attempt you MUST "
                                  u"save first and came back here again."),
            visible={'view': 'invisible', 'edit': 'visible'},
            columns={
                 'id' : SelectColumn(_(u"Column"),
                                     col_description=_('help_searchConfig_id',
                                                       default=u"The column on which you want to activate the search.\n"
                                                               u"Order matters."),
                                     vocabulary_factory="collective.tablepage.vocabulary.searchable_columns",
                                     required=True,
                                     default=""),
                 'label' : Column(_(u"Column label"),
                                  col_description=_('help_searchConfig_label',
                                                    default=u"The label to be used in the search form. "
                                                            u"Default is the column original label."),
                                  required=False),
                 'description' : TextAreaColumn(_(u"Column description"),
                                                col_description=_('help_searchConfig_description',
                                                                  default=u"A description to be used in search form"),),
                 'additionalConfiguration' : MultiSelectColumn(_(u"Additional features"),
                                                               col_description=_("search_additional_configuration",
                                                                                 default=u"Other options you can activate "
                                                                                         u"on the search"),
                                              vocabulary_factory="collective.tablepage.vocabulary.search_additional_options"),
            },
            condition="object/getPageColumns",
        ),
    ),


))


schemata.finalizeATCTSchema(TablePageSchema, moveDiscussion=False)

TablePageSchema.moveField('downloadEnabled', after='tableContents')

class TablePage(base.ATCTContent):
    """A document with an editable table"""

    implements(ITablePage)
    security = ClassSecurityInfo()

    meta_type = "TablePage"
    schema = TablePageSchema

    security.declareProtected(permissions.View, 'CookedBody')
    def CookedBody(self, stx_level='ignored'):
        """CMF compatibility method
        """
        return self.getText()

    security.declareProtected(permissions.ModifyPortalContent, 'EditableBody')
    def EditableBody(self):
        """CMF compatibility method
        """
        #return self.getRawText()
        return self.getText()

    security.declareProtected(permissions.View, 'getText')
    def getText(self, mimetype=None):
        """text field accessor"""
        text = ""
        if self.getTextBefore():
            text += self.getTextBefore()
        table_text = self.restrictedTraverse('@@view-table')()
        if table_text:
            text += "\n" + table_text.encode('utf-8')
        if self.getTextAfter():
            text += "\n" + self.getTextAfter()
        if mimetype:
            portal_transforms = getToolByName(self, 'portal_transforms')
            return str(portal_transforms.convertToData(mimetype, text))
        return text

    security.declarePrivate('validate_searchConfig')
    def validate_searchConfig(self, value):
        """Need to check table page ids"""
        ids = []
        for record in value:
            # do not validate the hidden empty row
            if record.get('orderindex_').isdigit():
                id = record.get('id', '')
                try:
                    ids.index(id)
                    return _('searchconfig_validation_error_duplicated_id',
                             default=u'The column "${col_name}" has already been used',
                             mapping={'col_name': id})
                except ValueError:
                        ids.append(id)

    security.declarePrivate('validate_pageColumns')
    def validate_pageColumns(self, value):
        """Need to check some table format"""
        ids = []
        for record in value:
            # do not validate the hidden empty row
            if record.get('orderindex_').isdigit():
                id = record.get('id', '')
                try:
                    ids.index(id)
                    return _('pagecolumn_validation_error_duplicated_id',
                             default=u'Id "${col_name}" is duplicated',
                             mapping={'col_name': id})
                except ValueError:
                        ids.append(id)
                if not re.match(r"^[a-zA-Z][a-zA-Z0-9.\-_]*$", id):
                    return _('pagecolumn_validation_error_id_format',
                             default=u'Invalid value: "${col_name}". "Column Id" must not contains special characters',
                             mapping={'col_name': id})
                if id in config.RESERVED_IDS:
                    return _('pagecolumn_validation_error_id_invalid',
                             default=u'A reserved value has been used for "id"')

    security.declareProtected(permissions.View, 'getCSSClassesVocabulary')
    def getCSSClassesVocabulary(self):
        utility = queryUtility(ITinyMCE)
        if utility:
            translation_service = getToolByName(self, 'translation_service')
            return atapi.DisplayList([[style.split('|')[1],
                                       translation_service.utranslate(msgid=style.split('|')[0],
                                                                      domain="plone.tinymce",
                                                                      context=self)] \
                            for style in utility.tablestyles.splitlines()])
        return tuple()

    security.declareProtected(permissions.ModifyPortalContent, 'setText')
    def setText(self):
        # for some reason, this is needed
        pass

    security.declarePublic('showHeadersVocabulary')
    def showHeadersVocabulary(self):
        return atapi.DisplayList(
            (('view_only', _("... only on page view")),
            ('edit_only', _("... only when editing table")),
            ('always', _("... always display"))),
        )

    security.declarePublic('insertTypeVocabulary')
    def insertTypeVocabulary(self):
        return atapi.DisplayList(
            (('append', _("At the end")),
            ('prepend', _("At the beginning"))),
        )

    def __bobo_traverse__(self, REQUEST, name):
        """Allows transparent access to rows"""
        if name.startswith('row-'):
            storage = IDataStorage(self)
            return storage[name[4:]]
        return super(TablePage, self).__bobo_traverse__(REQUEST, name)

atapi.registerType(TablePage, config.PROJECTNAME)
