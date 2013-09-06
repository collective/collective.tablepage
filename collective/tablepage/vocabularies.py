# -*- coding: utf-8 -*-

from zope.interface import implements
try:
    from zope.schema.interfaces import IVocabularyFactory
except ImportError:
    from zope.app.schema.vocabulary import IVocabularyFactory

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.component import getAdapters

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf

from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IColumnField
from collective.tablepage import logger

class ColumnTypesVocabulary(object):
    """Vocabulary factory for column types
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        #elements = ['String', 'Text', 'Select', 'File']
        adapters = getAdapters((context, context.REQUEST), IColumnField)
        elements = [a[0] for a in adapters]
        terms = [SimpleTerm(value=e, token=e, title=_(e)) for e in elements]
        return SimpleVocabulary(terms)

columnTypesVocabularyFactory = ColumnTypesVocabulary()
