# -*- coding: utf-8 -*-

import re

from zope.interface import implements
from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import base
from Products.ATContentTypes.configuration import zconf

from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.DataGridField.Column import Column

from collective.datagridcolumns.SelectColumn import SelectColumn
from collective.datagridcolumns.TextAreaColumn import TextAreaColumn

from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import ITablePage
from collective.tablepage import config

from Products.TinyMCE.interfaces.utility import ITinyMCE

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
        columns=("id", "label", "description", "type", "vocabulary", ),
        widget=DataGridWidget(
            label=_(u"Columns"),
            description=_('help_pageColumns',
                          default=u"Definition of rows inside the table"),
            visible={'view': 'invisible', 'edit': 'visible'},
            columns={
                 'id' : Column(_(u"Column id"), required=True),
                 'label' : Column(_(u"Column label"), required=True),
                 'description' : TextAreaColumn(_(u"Column description")),
                 'type' : SelectColumn(_(u"Type of data"),
                                       vocabulary_factory="collective.tablepage.vocabulary.column_types",
                                       required=True,
                                       default="String"),
                 'vocabulary' : TextAreaColumn(_(u"Vocabulary for the column"),
                                               col_description=_("vocabulary_column_description",
                                                                   default=u"One item on every row. "
                                                                           u"Used only when the type is \"Select\"")),
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

    # FOO FIELD!!!! Only needed to being able to use the ATReferenceBrowserWidget... :(
    atapi.StringField('link_internal',
            widget=ReferenceBrowserWidget(
                    label=u"Internal link dump field",
                    visible={'view': 'invisible', 'edit': 'invisible'},
                    force_close_on_insert=True,
                    startup_directory_method="this_directory",
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

atapi.registerType(TablePage, config.PROJECTNAME)
