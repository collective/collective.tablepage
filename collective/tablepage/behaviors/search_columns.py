# -*- coding: utf-8 -*-
from zope.interface import Interface
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.supermodel import model
from zope.interface import alsoProvides
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from collective.tablepage import tablepageMessageFactory as _
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema


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
                            u"Default is the column original label."),
        required=False,
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


class ITableSearchRow(model.Schema):

    searchConfig = schema.List(
        title=_(u"Search configuration"),
        description=_('help_searchConfig',
                    default=u"Provide configuration for the search in table.\n"
                            u"Please note that this section will not load live data from the \"Columns\" field. "
                            u"If you changed something in the columns configuration during this edit attempt you MUST "
                            u"save first and came back here again."),
        required=False,
        value_type=DictRow(
            schema=ISearchConfigRow
        )
    )
    form.widget(searchConfig=DataGridFieldFactory)

fieldset = Fieldset(
    'search',
    label=_(u'Search'),
    fields=['searchConfig']
)
ITableSearchRow.setTaggedValue(FIELDSETS_KEY, [fieldset])


class TableSearchRow(model.Schema):

    ''' Behavior interface
    '''

alsoProvides(ITableSearchRow, IFormFieldProvider)