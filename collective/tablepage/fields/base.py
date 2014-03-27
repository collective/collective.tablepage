# -*- coding: utf-8 -*-

import sys
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getUtility
from collective.tablepage.interfaces import IColumnDataRetriever
from zope.schema.interfaces import IVocabularyFactory

if sys.version_info < (2, 6):
    PLONE3 = True
else:
    PLONE3 = False


class BaseField(object):
    """Generic class for all columns"""

    # not implemented; subclasses must change this
    edit_template = None
    view_template = None
    # By default we don't need cache
    cache_time = 0

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = None
        self.configuration = None

    def render_edit(self, data):
        data = data or ''
        if isinstance(data, basestring):
            # on validation error we can get a FileUpload instance
            self.data = data.decode('utf-8')
        return self.edit_template(data=self.data)

    def render_view(self, data, index=None):
        self.data = data or ''
        return self.view_template(data=self.data)

    def _getCustomPreferences(self):
        """Override some preferences when displaying the linkable content
        @title will override the linked content title
        @icon an URL or relative path to an icon resource. When present, this will be used inside the link
        to be downloaded (not text will be shown) 
        """
        prefs = {}
        conf = self.configuration.get('vocabulary') or ''
        for c in conf.splitlines():
            if c.startswith('title:'):
                prefs['title'] = c[6:]
            elif c.startswith('icon:'):
                prefs['icon'] = c[5:]
        return prefs

    def _get_obj_info(self, uuid):
        # for fields that need to refer to other contents
        rcatalog = getToolByName(self.context, 'reference_catalog')
        obj = rcatalog.lookupObject(uuid)
        if obj:
            custom_prefs = self._getCustomPreferences()
            # BBB: final slash below is important for Plone 3.3 compatibility
            # remove this mess when finally we drop Plone 3.3 support
            RESOLVE_UID_STR = "resolveuid/%s"
            if PLONE3:
                RESOLVE_UID_STR += '/'
            return dict(title=custom_prefs.get('title') or obj.Title() or obj.getId(),
                        url=RESOLVE_UID_STR % uuid,
                        description=obj.Description(),
                        icon=obj.getIcon(relative_to_portal=1),
                        main_icon=custom_prefs.get('icon'))
        return {}

    @property
    def options(self):
        """Read configuration options as dict"""
        factory = getUtility(IVocabularyFactory, 'collective.tablepage.vocabulary.row_options')
        vocabulary = factory(self.context)

        options = {}
        for term in vocabulary:
            options[term.value] = term.value in self.configuration.get('options', [])
        return options


class BaseFieldDataRetriever(object):
    """Get data from the request, return it. Nothing more"""

    implements(IColumnDataRetriever)

    def __init__(self, context):
        self.context = context
        self.configuration = None

    def get_from_request(self, name, request):
        if request.get(name) is not None:
            return {name: request.get(name)}
        return None

    def data_for_display(self, data, backend=False, row_index=None):
        """Default implementation... just return data""" 
        return data

    def data_to_storage(self, data):
        """Default implementation... just return data (stripped)"""
        return data and data.strip() or None
