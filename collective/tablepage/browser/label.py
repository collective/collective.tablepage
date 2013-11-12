# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from plone.memoize.view import memoize
from collective.tablepage import config
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IDataStorage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

try:
    from Products.CMFEditions.utilities import isObjectChanged
    from Products.CMFEditions.utilities import maybeSaveVersion
    from Products.CMFEditions.utilities import isObjectVersioned
    VERSIONING_SUPPORT = True
except ImportError:
    # No versioning support for Plone 3.3 version of CMFEditions
    VERSIONING_SUPPORT = False

class EditLabelView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        request.set('disable_border', True)
        self.configuration = self.context.getPageColumns()
        self.data = ''

    def _addNewVersion(self, comment=''):
        """Content must be updated, so the history machinery will save a new version"""
        context = self.context
        context.reindexObject()
        if VERSIONING_SUPPORT and isObjectChanged(context) and isObjectVersioned(context):
            maybeSaveVersion(context, comment=comment)

    def check_labeling_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission(config.MANAGE_LABEL, self.context)

    @property
    @memoize
    def storage(self):
        return IDataStorage(self.context)

    def _save(self):
        form = self.request.form
        context = self.context
        label = form.get('label')
        _ = getToolByName(context, 'translation_service').utranslate
        if form.get('row-index') is not None and form.get('addLabel'):
            # adding new but not in the last line
            index = form.get('row-index')
            self.storage.add({'__label__': label}, index)
            self._addNewVersion(_(msgid="Label added",
                                  domain="collective.tablepage",
                                  context=context))
        elif form.get('row-index') is not None:
            # updating label
            index = form.get('row-index')
            self.storage.update(index, {'__label__': label})
            self._addNewVersion(_(msgid="Label changed",
                                  domain="collective.tablepage",
                                  context=context))
        else:
            self.storage.add({'__label__': label})
            self._addNewVersion(_(msgid="Label added",
                                  domain="collective.tablepage",
                                  context=context))

    def __call__(self, *args, **kwargs):
        request = self.request
        form = request.form
        putils = getToolByName(self.context, 'plone_utils')
        if not self.check_labeling_permission():
            raise Unauthorized("You can't modify the label")
        if form.get('cancel'):
            return request.response.redirect("%s/edit-table" % self.context.absolute_url())
        if form.get('form.submitted'):
            if not form.get('label'):
                putils.addPortalMessage(_('Label is required'), type="error")
                return request.response.redirect("%s/edit-label" % self.context.absolute_url())
            # saving
            self._save()
            putils.addPortalMessage(_('Label has been saved'))
            return request.response.redirect("%s/edit-table" % self.context.absolute_url())
        elif form.get('row-index') is not None:
            # load an existing row
            self.data = self.storage[form.get('row-index')].get('__label__', '')
        return self.index()
