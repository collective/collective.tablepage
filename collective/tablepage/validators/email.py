# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from collective.tablepage.interfaces import IFieldValidator
from collective.tablepage import tablepageMessageFactory as _


class ValidatorIsEmail(object):
    """Validate that submitted data is an email"""
    implements(IFieldValidator)

    def __init__(self, field):
        self.field = field

    def validate(self, configuration, data=None):
        data = data or self.field.request.form.get(configuration['id'], '')
        if data:
            ptool = getToolByName(self.field.context, 'plone_utils')
            if ptool.validateEmailAddresses(data):
                return
            return _('error_field_not_email', default='The field "$name" is not a valid e-mail address',
                     mapping={'name': configuration.get('label', configuration['id']).decode('utf-8')})
