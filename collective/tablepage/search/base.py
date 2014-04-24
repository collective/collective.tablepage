# -*- coding: utf-8 -*-


class BaseSearch(object):

    def __init__(self):
        self.id = None
        self.context = None
        self.request = None
        self.label = None
        self.description = None
        self.configuration = None
        self.search_configuration = None

    def check_configuration(self, key):
        """Check if a configuration is activated"""
        return key in self.search_configuration.get('additionalConfiguration')
