# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.i18n import translate
from collective.tablepage.fields.interfaces import INumberColumnField
from collective.tablepage.fields.interfaces import IMonetaryColumnField
from collective.tablepage.fields.text import TextField
from collective.tablepage import tablepageMessageFactory as _

try:
    from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
except ImportError:
    # Plone < 4.1
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile



class NumberField(TextField):
    implements(INumberColumnField)

    edit_template = ViewPageTemplateFile('templates/number.pt')


class MonetaryField(NumberField):
    implements(IMonetaryColumnField)

    # from http://stackoverflow.com/questions/5963158/html5-form-input-pattern-currency-format
    # replace with the better alternatives as soon as Plone 3.3. will be dropped
    def intWithCommas(self, x):
        if x < 0:
            return '-' + self.intWithCommas(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            thousand_separator = translate(_('thousand_separator',
                                             default=","),
                                            context=self.request)
            result = "%s%03d%s" % (thousand_separator, r, result)
        return "%d%s" % (x, result)


    def render_view(self, data, index=None):
        """When in view, render data in the proper monetary (and localized) format"""
        self.data = data or ''
        if self.data:
            
            try:
                float(self.data)
            except ValueError:
                # Do not continue
                return self.data
            
            parts = self.data.split('.')
            try:
                i_data = int(parts[0])
            except ValueError:
                return self.view_template(data='')
            i_data = self.intWithCommas(i_data)

            if len(parts)>1:
                dec_data = parts[1]
            else:
                dec_data = '00'
            if len(dec_data)<2:
                dec_data = dec_data + "0"
            dec_data = dec_data[0:2]

            decimal_separator = translate(_('decimal_separator',
                                             default="."),
                                          context=self.request)
            monetary_sign = translate(_('monetary_sign',
                                        default="$"),
                                      context=self.request)

            self.data = "%s %s%s%s" % (monetary_sign, i_data, decimal_separator, dec_data)
            return self.view_template(data=self.data)
        return ''
