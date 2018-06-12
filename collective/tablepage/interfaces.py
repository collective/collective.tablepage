# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute
from plone.supermodel import model
from collective.tablepage import tablepageMessageFactory as _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from zope import schema
from zope.interface import Interface
from plone.autoform import directives as form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.app.textfield import RichText
from z3c.relationfield.schema import RelationChoice
from zope.schema.vocabulary import SimpleTerm                                    
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import invariant, Invalid
from collective.tablepage import config
import re


showHeadersVocabulary = SimpleVocabulary([                                                      
    SimpleTerm(
        value='view_only', 
        title=_("... only on page view")
    ),  
    SimpleTerm(
        value='edit_only', 
        title=_("... only when editing table")
    ),
    SimpleTerm(
        value='always', 
        title=_("... always display")
    ),
]) 

insertTypeVocabulary = SimpleVocabulary([
    SimpleTerm(
        value='append', 
        title=_("At the end")
    ),  
    SimpleTerm(
        value='prepend', 
        title=_("At the beginning")
    ),  
])

class IColumnField(Interface):
    """An object able to render an widget for handling data from a column"""

    configuration = Attribute("""Columns configuration""")
    cache_time = Attribute("""Integer value, in seconds, for determining if and how the column render will be cached""")

    def render_edit(data):
        """
        Get the HTML field for editing. This can be None, and the field will not be rendered on editing row
        """

    def render_view(data, index=None, storage=None):
        """Get the HTML field for final display
        @index the row index of the data in the table
        @storage data storage to be used
        """


class IDataStorage(Interface):
    """An object able to store table data inside Plone contents"""

    def __getitem__(index):
        """Get an item from the storage, by index"""

    def __delitem__(index):
        """Delete an item from the storage, by index"""

    def __len__():
        """Items in the storage"""

    def clear():
        """Clear all storage data"""

    def add(data, index=-1):
        """Add data to the storage. Data must the a dict-like structure"""

    def update(index, data):
        """Update data stored at given row"""

    def nullify(index, key):
        """Delete a single row subitem"""


class IColumnDataRetriever(Interface):
    """An object that can handle data stored (or to be stored) inside the IDataStorage"""

    def get_from_request(name, request):
        """Read data from the request and return a {id: value} dict, or None
        The scope of the method is to obtain data in the proper format, that is commonly a string
        """

    def data_for_display(data, backend=False, row_index=None):
        """Transform data, to be displayed outside Plone (commonly: to CSV)
        @backend specify that data is for backend purpose
        @row_index index of the row were extraction is taking place
        """

    def data_to_storage(data):
        """Sanitize data that came outside Plone before save it to storage.
        This is commonly called by the CSV import utility, to know how to handle a single CSV entry
        """


class IFieldValidator(Interface):
    """A validator for the submitted data"""

    def validate(configuration, data=None):
        """Validate input data
        @param configuration TablePage configuration
        @data data to be validated (commonly taken from the request)
        @return the error message (if any) or None
        """

class ITableRow(Interface):

    id = schema.TextLine(
        title=_(u"Column id"),
        required=True
    )

    label = schema.TextLine(
        title=_(u"Column label"),
        required=True
    )

    description = schema.Text(
        title=_(u"Column description"),
        required=False
    )

    type = schema.Choice(
        title=_(u"Type of data"),
        required=True,
        default="String",
        vocabulary="collective.tablepage.vocabulary.column_types",
    )

    vocabulary = schema.Text(
        title=_(u"Column configuration"),
        required=False,
        description=_("vocabulary_column_description",
                default=u"Some columns types will need this.\n"
                u"For \"Select\" type: used for defining the "
                u"vocabulary (one item on per row).\n"
                u"For \"Computed\" type: write there the TALES expression."),
    )

    options = schema.Tuple(
        title=_("options_column_description",
                default=u"Other options you can activate on the column"),
        description=_("options_column_description",
                    default=u"Other options you can activate on the column"),
        required=False,
        missing_value=(),
        value_type=schema.Choice(
            source="collective.tablepage.vocabulary.row_options"
        )
    )
    form.widget(options=CheckBoxFieldWidget)


class ISearchConfigRow(Interface):

    id = schema.Choice(
        title=_(u"Search configuration"),
        description=_('help_searchConfig',                                   
                    default=u"Provide configuration for the search in table.\n"
                            u"Please note that this section will not load live data from the \"Columns\" field. "
                            u"If you changed something in the columns configuration during this edit attempt you MUST "
                            u"save first and came back here again."),
        required=True,
        default="",
        vocabulary="collective.tablepage.vocabulary.searchable_columns",
    )

    label = schema.TextLine(
        title=_(u"Column label"), 
        description=_('help_searchConfig_label',   
                    default=u"The label to be used in the search form. "
                            u"Default is the column original label.")
    )
    description = schema.Text(
        required=False,
        title=_(u"Column description"),        
        description=_('help_searchConfig_description',
                     default=u"A description to be used in search form"),
    )

    additionalConfiguration = schema.Tuple(
        title=_(u"Additional features"),
        description=_("options_column_description",
                    default=u"Other options you can activate on the column"),
        required=False,
        missing_value=(),
        value_type=schema.Choice(
            source="collective.tablepage.vocabulary.search_additional_options"
        )
    )
    form.widget(options=CheckBoxFieldWidget)

class ITablePage(model.Schema):
    """ Marker interface and Dexterity Python Schema for Tablepage
    """

    textBefore = RichText(
        title=_(u'label_text_before', default=u'Text before the table'),
        required=False
    )

    pageColumns = schema.List(
        title=_(u"Columns"),
        description=_('help_pageColumns', default=u"Definition of rows inside the table"),
        required=False,
        value_type=DictRow(
            schema=ITableRow
        )
    )
    form.widget(pageColumns=DataGridFieldFactory)

    tableCaption = schema.TextLine(
        title=_(u'Table caption'),
        required=False,
        description=_('help_table_caption',
                       default=u'Optional summary of table contents'),
    )

    cssClasses = schema.Tuple(
        title=_(u'CSS classes'),
        description=_(u'CSS classes to be applied to the table.\n'
                      u'This list is taken from available TinyMCE style for tables.'),
        default=("listing",),
        required=False,
        missing_value=(),
        value_type=schema.Choice(
            source="collective.tablepage.vocabulary.css_classes"
        )
    )
    form.widget(cssClasses=CheckBoxFieldWidget)

    textAfter = RichText(
        title=_(u'label_text_after', default=u'Text after the table'),
        required=False
    )

    attachmentStorage = RelationChoice(
        title=_(u"Attachment storage"),
        description=_('attachmentStorage_help',
            default=u"Select the folder where users will be able to store attachments for "
                u"attachment-like columns (if any).\n"
                u"Users must be able to add new contents on that folder; if not, they "
                u"will be only able to select existings items.\n"
                u"If not provided, the folder containing this document will be used."),
        vocabulary='plone.app.vocabularies.Catalog',
        required=False,
    )


    downloadEnabled = schema.Bool(
        title=_(u'Show download link for data'),
        description=_('help_download_enabled',
                      default=u'Display a download link for data inside the table in CSV format'),
        required=False
    )

    showHeaders = schema.Choice(
        title=_(u"Type of data"),
        description=_(u'Show table headers when...'),
        required=False,
        default="always",
        vocabulary=showHeadersVocabulary,
    )

    insertType = schema.Choice(
        title=_(u'Criteria for adding new rows'),
        description=_('help_insertType',                         
                      default=u'Criteria of inserting new row.\n'
                              u'Choose if add row at the end of group (append) '
                              u'or before group (prepend).'),    
        required=False,
        default="append",
        vocabulary=insertTypeVocabulary,
    )

    batchSize = schema.Int(
        title=_(u'Max number of rows'),
        description=_('help_batchSize',                          
                        default=u'Insert the maximum number of rows to be displayed '
                                u'in a single page.\n'             
                                u'When this limit is reached a batching navigation section '
                                u'will be displayed.\n'            
                                u'Use 0 to disable batching (NOT suggested on very large tables or '
                                u'extremly complex column types).'
        ),
        default=100,
    )

    # searchConfig = schema.List(
    #     title=_(u"Search configuration"),
    #     description=_('help_searchConfig',                                   
    #                 default=u"Provide configuration for the search in table.\n"
    #                         u"Please note that this section will not load live data from the \"Columns\" field. "
    #                         u"If you changed something in the columns configuration during this edit attempt you MUST "
    #                         u"save first and came back here again."), 
    #     required=False,
    #     value_type=DictRow(
    #         schema=ISearchConfigRow
    #     )
    # )
    # form.widget(searchConfig=DataGridFieldFactory)

    model.fieldset(
        'settings',
        label=u"Settings",
        fields=[
            'downloadEnabled',
            'showHeaders',
            'insertType',
            'batchSize',
        ]
    )

    # model.fieldset(
    #     'search',
    #     label=u"Search",
    #     fields=[
    #         'searchConfig',
    #     ]
    # )
