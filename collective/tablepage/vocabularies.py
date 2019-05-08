# -*- coding: utf-8 -*-

try:
    from zope.schema.interfaces import IVocabularyFactory
except ImportError:
    from zope.app.schema.vocabulary import IVocabularyFactory

from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.search.interfaces import ISearchableColumn
from zope.component import getUtilitiesFor
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.dexterity.interfaces import IDexterityContent
from zope.globalrequest import getRequest


class ColumnTypesVocabulary(object):
    """Types of columns vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        #import pdb; pdb.set_trace()
        items = [
            (u'CIG', _(u'CIG')),
            (u'Struttura proponente', _(u'Struttura proponente')),
            (u'Oggetto', _(u'Oggetto')),
            (u'Procedura scelta contraente', _(u'Procedura scelta contraente')),
            (u'Operatori / Aggiudicatari', _(u'Operatori / Aggiudicatari')),
            (u'Dal-Al', _(u'Dal-Al')),
            (u'Computed', _(u'Computed')),
            (u'Link', _(u'Link')),
            (u'Date', _(u'Date')),
            (u'Date/Time', _(u'Date/Time')),
            (u'Email', _(u'Email')),
            (u'File', _(u'File')),
            (u'Monetary', _(u'Monetary')),
            (u'Numeric', _(u'Numeric')),
            (u'Files', _(u'Files')),
            (u'Select', _(u'Select')),
            (u'String', _(u'String')),
            (u'Text', _(u'Text')),
        ]
        terms = [SimpleTerm(value=e[0], token=e[0], title=e[1]) for e in items]
        return SimpleVocabulary(terms)


class RowOptionsVocabulary(object):
    """Column's options vocavulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = [
                 SimpleTerm(value='required', token='required', title=_('row_options_required',
                                                                        default=u'Required')),
                 SimpleTerm(value='unique', token='unique', title=_('row_options_unique',
                                                                        default=u'Unique')),
#                 SimpleTerm(value='enforceVocabulary', token='enforceVocabulary', title=_('row_options_enforceVocabulary',
#                                                                                          default=u'Fulfil vocabulary')),
                 ]
        return SimpleVocabulary(terms)


class SearchableColumnsVocabulary(object):
    """All searchable columns inside a table page
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]
        configuration = getattr(context, 'pageColumns', [])
        adaptables = [x[0] for x in getUtilitiesFor(ISearchableColumn)]
        terms = [SimpleTerm(value='SearchableText', token='SearchableText', title=_(u'Search in text'))]
        for conf in configuration:
            if conf['type'] in adaptables:
                terms.append(SimpleTerm(value=conf['id'], token=conf['id'], title=conf['label']))
        return SimpleVocabulary(terms)


class SearchAdditionalOptionsVocabulary(object):
    """Additional search options
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        terms = [SimpleTerm(value='SearchableText', token='SearchableText',
                            title=_(u'Use in full text search')),
                 SimpleTerm(value='single_value', token='single_value',
                            title=_(u'Single value search')),
                 ]
        return SimpleVocabulary(terms)


class CSSClassesVocabulary(object):
    implements(IVocabularyFactory)

    def get_table_styles(self):
        registry = getUtility(IRegistry)
        styles = registry['plone.table_styles']
        if not styles:
            return []
        else:
            return [
                SimpleTerm(
                    token=style.split('|')[1],
                    value=style.split('|')[1],
                    title=style.split('|')[0])
                for style in styles
            ]

    def __call__(self, context):
        return SimpleVocabulary(self.get_table_styles())


columnTypesVocabularyFactory = ColumnTypesVocabulary()
rowOptionsVocabularyFactory = RowOptionsVocabulary()
searchableColumnsVocabularyFactory = SearchableColumnsVocabulary()
searchAdditionalOptionsVocabularyFactory = SearchAdditionalOptionsVocabulary()
CSSClassesFactory = CSSClassesVocabulary()
