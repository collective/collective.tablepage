# -*- coding: utf-8 -*-

from collective.tablepage.search.text import TextSearch


class SelectSearch(TextSearch):
    
    def index_values(self):
        """Read vocabulary from... vocabulary!"""
        vocabulary = self.configuration.get('vocabulary') or ''
        return vocabulary.splitlines()
