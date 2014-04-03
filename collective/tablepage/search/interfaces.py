# -*- coding: utf-8 -*-

from zope.interface import Interface

class ISearchableColumn(Interface):
    """Define an object able to provide search support for collective.tablepage columns"""
