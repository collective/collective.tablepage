# -*- coding: utf-8 -*-

from zope.interface import implements
from collective.tablepage.interfaces import IFieldValidator
from collective.tablepage import tablepageMessageFactory as _
from collective.tablepage.interfaces import IDataStorage


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
                     mapping={'name': configuration.get('label', configuration['id']).decode('utf-8')})


class ValidatorUnique(object):
    """Validate that data is unqie inside the column"""
    implements(IFieldValidator)

    def __init__(self, field):
        self.field = field

    def validate(self, configuration):
        if 'unique' not in configuration['options']:
            return None
        col_id = configuration['id']
        data = self.field.request.form.get(col_id)
        if data:
            context = self.field.context
            storage = IDataStorage(context)
            for row in storage:
                if row.get(col_id)==data:
                    return _('error_field_unique', default='The value "$value" is already present in the column \"$name\"',
                             mapping={'name': configuration.get('label', col_id).decode('utf-8'),
                                      'value': data.decode('utf-8')})
