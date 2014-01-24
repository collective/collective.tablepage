# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.interfaces import IFieldValidator
from collective.tablepage import tablepageMessageFactory as _


class ValidatorIsNumeric(object):
    """Validate that submitted data is an number"""
    implements(IFieldValidator)

    def __init__(self, field):
        self.field = field

    def validate(self, configuration, data=None):
        data = data or self.field.request.form.get(configuration['id'], '')
        if data:
            try:
                float(data)
                return
            except ValueError:
                return _('error_field_not_number', default='The value "$value" is not numeric',
                         mapping={'value': data.decode('utf-8')})
