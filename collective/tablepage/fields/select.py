# -*- coding: utf-8 -*-

from Products.PageTemplates import Expressions
from zope.interface import implements
from collective.tablepage.fields.interfaces import ISelectColumnField
from collective.tablepage.fields.base import BaseField
from zope.tales.tales import CompilerError
from zope.component import getMultiAdapter
from collective.tablepage import logger


try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class SelectField(BaseField):
    implements(ISelectColumnField)

    edit_template = ViewPageTemplateFile('templates/select.pt')
    view_template = ViewPageTemplateFile('templates/string_view.pt')

    def vocabulary(self):
        """Vocabulary can be a static list of values, or a vocabulary:TAL espression"""
        raw_vocabulary = self.configuration.get('vocabulary')
        values = raw_vocabulary.rstrip().decode('utf-8').splitlines()
        talEngine = Expressions.getEngine()
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        evals = {
            'portal': portal_state.portal(),
            'context': self.context,
            'request': self.request,
        }

        results = []
        for value in values:
            if value and value.startswith('vocabulary:'):
                tales = value[11:]    
                try:
                    compiledExpr = talEngine.compile(tales)
                    result = compiledExpr(talEngine.getContext(evals))
                    results.extend(result)
                except CompilerError, e:
                    logger.error("Error compiling %s: %s" % (tales, e))
                    continue
                except Exception, e:
                    logger.error("Error evaluating %s: %s" % (tales, e))
                    continue
            else:
                results.append(value)
        return results
