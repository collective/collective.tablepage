# -*- coding: utf-8 -*-

from collective.tablepage.interfaces import IColumnField


class ITextColumnField(IColumnField):
    """A column field that handle simple short text"""

class ITextAreaColumnField(ITextColumnField):
    """A column field that handle text"""

class IEmailColumnField(ITextColumnField):
    """A column field that handle only text in email format"""

class INumberColumnField(ITextColumnField):
    """A column field that handle only text in numeric format"""

class ISelectColumnField(ITextColumnField):
    """A column field that handle text"""

class ILinkColumnField(IColumnField):
    """A column field that handle link"""

class IFileColumnField(IColumnField):
    """A column field that handle file upload or selection"""

class IMultiFileColumnField(IColumnField):
    """A column field that handle set of files, to be uploaded or selected"""
