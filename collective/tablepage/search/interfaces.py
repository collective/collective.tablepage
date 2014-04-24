# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class ISearchableColumn(Interface):
    """Define an object able to provide search support for collective.tablepage columns"""

    id = Attribute("""Id of the field""")
    configuration = Attribute("""configuration of the column in the table page""")
    search_configuration = Attribute("""configuration of the search settings for the column""")
    context = Attribute("""Current context (tablepage)""")
    request = Attribute("""Current request""")
    label = Attribute("""Label to be displayed for the form""")
    description = Attribute("""Help description for filling the form""")

    def render(meta_type=None):
        """Return the field HTML"""
