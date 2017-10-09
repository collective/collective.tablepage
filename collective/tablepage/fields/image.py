# -*- coding: utf-8 -*-

from collective.tablepage.fields.interfaces import IImageColumnField
from zope.interface import implements
from .file import FileField

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

TYPE_TO_CREATE = 'Image'

try:
    from plone.dexterity.interfaces import IDexterityContent
    from plone.namedfile.file import NamedBlobImage
    HAS_DEXTERITY = True
except ImportError:
    HAS_DEXTERITY = False
    IDexterityContent = None
    NamedBlobImage = None

from .file import FileDataRetriever

class ImageField(FileField):
    implements(IImageColumnField)
    portal_type = TYPE_TO_CREATE
    field_value_class = NamedBlobImage

    edit_template = ViewPageTemplateFile('templates/image.pt')
    view_template = ViewPageTemplateFile('templates/image_view.pt')

    def _get_obj_info(self, uuid):
        info = super(ImageField, self)._get_obj_info(uuid)
        preferences = self._getCustomPreferences()
        if preferences.get('size', None):
            size = preferences['size']
        else:
            size = 'tile'

        if 'url' in info:
            url = info['url'].rstrip('/')
            if HAS_DEXTERITY and IDexterityContent.providedBy(info['object']):
                thumbnail_url = url + '/@@images/image/' + size
            else:
                thumbnail_url = url + '/image_' + size

            info['thumbnail_url'] = thumbnail_url
        return info

    def _getCustomPreferences(self):
        """Override some preferences when displaying the linkable content
        @size will override image size displayed
        """
        prefs = super(ImageField, self)._getCustomPreferences()
        conf = self.configuration.get('vocabulary') or ''
        for c in conf.splitlines():
            if c.startswith('size:'):
                prefs['size'] = c.split(':', 1)[1]

        return prefs


class ImageDataRetriever(FileDataRetriever):
    portal_type = TYPE_TO_CREATE
    field_name = 'image'
    field_value_class = NamedBlobImage
