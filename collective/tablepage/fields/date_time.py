# -*- coding: utf-8 -*-

from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from Products.CMFCore.utils import getToolByName
from collective.tablepage.fields.base import BaseField
from collective.tablepage.fields.base import BaseFieldDataRetriever
from collective.tablepage.fields.interfaces import IDateTimeColumnField
from zope.component import getMultiAdapter
from zope.interface import implements

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


class DateField(DateTimeField):
    """A field that store date formatted string"""
    show_hm = False


class DateTimeDataRetriever(BaseFieldDataRetriever):
    """Get data from the request, return it as a date"""

    show_hm = True

    def __init__(self, context):
        self.context = context
        self.configuration = None

    def get_from_request(self, name, request):
        """Return data only if is a real date formatted string"""
        
        datestr = "%(year)s-%(month)s-%(day)s" % {'year': request.get("%s_year" % name),
                                                  'month': request.get("%s_month" % name),
                                                  'day': request.get("%s_day" % name),
                                                  }
        if self.show_hm:
            timestr = "%(hour)s:%(minute)s:00" % {'hour': request.get("%s_hour" % name),
                                                   'minute': request.get("%s_minute" % name),
                                                   }
            datestr = datestr + ' ' + timestr

        try:
            return {name: DateTime(datestr).strftime('%Y-%m-%d %H:%M:%S')}
        except DateTimeError:
            pass
        return None

    def data_for_display(self, data, backend=False, row_index=None):
        """Default implementation... just return data""" 
        return DateTime(data)

    def data_to_storage(self, data):
        """Default implementation... just return data (stripped)"""
        return data and data.strip() or None


class DateDataRetriever(DateTimeDataRetriever):
    show_hm = False
