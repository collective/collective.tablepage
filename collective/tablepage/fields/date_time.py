# -*- coding: utf-8 -*-

from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from Products.CMFPlone import utils
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.base import BaseFieldDataRetriever
from collective.tablepage.fields.interfaces import IDateTimeColumnField
from zope.component import getMultiAdapter
from zope.interface import implements
from datetime import datetime

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class DateTimeField(BaseField):
    """A field that store date-time formatted string"""
    implements(IDateTimeColumnField)

    edit_template = ViewPageTemplateFile('templates/datetime.pt')
    view_template = ViewPageTemplateFile('templates/string_view.pt')

    show_hm = True

    @classmethod
    def RealIndexIterator(csl):
        # Plone 3 compatibility
        return utils.RealIndexIterator(pos=0)

    def render_view(self, data, index=None, storage=None):
        self.data = data or ''
        if self.data:
            try:
                date = DateTime(self.data)
                ploneview = getMultiAdapter((self.context, self.request), name=u'plone')
                self.data = ploneview.toLocalizedTime(date, long_format=self.show_hm)
            except DateTimeError:
                self.data = ''
        return self.view_template(data=self.data)
 
    def render_edit(self, data):
        # trying to keep the same date/time format used in P4,
        # we need to elaborate the data
        self.data = data and data[:-3].replace('/', '-') or ''
        return self.edit_template(data=self.data)


class DateField(DateTimeField):
    """A field that store date formatted string"""
    show_hm = False

    def render_edit(self, data):
        # trying to keep the same date/time format used in P4,
        # we need to elaborate the data
        self.data = data and data[:-9].replace('/', '-') or ''
        return self.edit_template(data=self.data)


class DateTimeDataRetriever(BaseFieldDataRetriever):
    """Get data from the request, return it as a date"""

    show_hm = True

    def __init__(self, context):
        self.context = context
        self.configuration = None

    def get_from_request(self, name, request):
        """Return data only if is a real date formatted string"""
        # using mockup arrives something like: '2018-06-12 09:50'
        value = request.get(name)
       
        if not value:
            return {name: None}

        # let's try to keep data the more similar to the plone4 code version
        if not self.show_hm:
            value = value + ' 00:00:00'
        else:
            value = value + ':00'

        # except that now we ships a datetime
        datetime_object = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

        try:
            return {name: datetime_object.strftime('%Y/%m/%d %H:%M:%S')}
        except Exception:
            pass
        return {name: None}

    def data_for_display(self, data, backend=False, row_index=None):
        """Return the data formatted in the propert locales format"""
        if backend:
            return data 
        ploneview = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone')
        return ploneview.toLocalizedTime(data, long_format=self.show_hm)

    def data_to_storage(self, data):
        """Try to convert data to a datetime"""
        data = data and data.strip() or ''
        try:
            DateTime(data)
        except DateTimeError:
            return None
        return data


class DateDataRetriever(DateTimeDataRetriever):
    show_hm = False
