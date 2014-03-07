# -*- coding: utf-8 -*-

try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from collective.tablepage.fields.computed.interfaces import IComputedColumnHandler


class BaseHandler(object):
    """Base implementation: just return the stored data"""
    implements(IComputedColumnHandler)

    def __call__(self, data):
        return data


class FileHandler(object):
    """Handler for File: a File content"""
    implements(IComputedColumnHandler)

    def __call__(self, data):
        # data is a file uuid
        rcatalog = getToolByName(getSite(), 'reference_catalog')
        obj = rcatalog.lookupObject(data)
        if not obj:
            return None
        return obj


class MultiFilesHandler(object):
    """Handler for multiple files: an array of File contents"""
    implements(IComputedColumnHandler)

    def __call__(self, data):
        # data is a set of uuids to files
        if not data:
            return None
        rcatalog = getToolByName(getSite(), 'reference_catalog')
        uuids = data.splitlines()
        results = []
        for uuid in uuids:
            obj = rcatalog.lookupObject(uuid)
            if not obj:
                continue
            results.append(obj)
        return results


class LinkHandler(object):
    """Handler for Link columns: Plone content or URL"""
    implements(IComputedColumnHandler)

    def __call__(self, data):
        # data can be an uuid
        rcatalog = getToolByName(getSite(), 'reference_catalog')
        obj = rcatalog.lookupObject(data)
        if not obj:
            return data
        return obj
