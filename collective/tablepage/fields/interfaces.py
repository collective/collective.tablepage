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

class IMonetaryColumnField(INumberColumnField):
    """A column field that handle only text in numeric format, but for display monetary values"""

class ISelectColumnField(ITextColumnField):
    """A column field that handle text"""

class ILinkColumnField(IColumnField):
    """A column field that handle link"""

class IFileColumnField(IColumnField):
    """A column field that handle file upload or selection"""

class IMultiFileColumnField(IColumnField):
    """A column field that handle set of files, to be uploaded or selected"""

class IComputedColumnField(IColumnField):
    """A column field that handle a TAL expression, for taking data from other columns value or site's documents"""
