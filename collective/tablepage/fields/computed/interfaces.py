# -*- coding: utf-8 -*-

from zope.interface import Interface

class IComputedColumnHandler(Interface):
    """A callable object able to handle row data for computed fields"""
