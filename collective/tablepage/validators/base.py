# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.interfaces import IFieldValidator
from collective.tablepage import tablepageMessageFactory as _


class ValidatorRequired(object):
    """Validate that some data has been submitted"""
    implements(IFieldValidator)

    def __init__(self, field):
        self.field = field

    def validate(self, configuration):
        if 'required' not in configuration['options']:
            return None
        if not self.field.request.form.get(configuration['id']):
            return _('error_field_required', default='The field "$name" is required',
                     mapping={'name': configuration.get('label', configuration['id'])})
