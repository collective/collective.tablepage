# -*- coding: utf-8 -*-

try:
    from zope.schema.interfaces import IVocabularyFactory
except ImportError:
    from zope.app.schema.vocabulary import IVocabularyFactory

from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IColumnField
from zope.component import getAdapters
from zope.i18n import translate
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class ColumnTypesVocabulary(object):
    """Types of columns vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        request = context.REQUEST
        adapters = getAdapters((context, context.REQUEST), IColumnField)
        elements = [a[0] for a in adapters]
        elements.sort(cmp=lambda x,y: cmp(translate(_(x), context=request),
                                          translate(_(y), context=request)))
        terms = [SimpleTerm(value=e, token=e, title=_(e)) for e in elements]
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


columnTypesVocabularyFactory = ColumnTypesVocabulary()
rowOptionsVocabularyFactory = RowOptionsVocabulary()