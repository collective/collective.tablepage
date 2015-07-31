# -*- coding: utf-8 -*-

import unittest
from collective.tablepage.validators.base import ValidatorEnforceVocabulary 
#from collective.tablepage.testing import TABLE_PAGE_INTEGRATION_TESTING


class FakeField(object):
    
    def __init__(self):
        self.configuration = None
        self._vocabulary = []

    def vocabulary(self):
        return [x.decode('utf-8') for x in self._vocabulary]


class BaseValidatorTestCase(unittest.TestCase):
    
    def setUp(self):
        self.field = FakeField()
    
    def test_ValidatorEnforceVocabulary(self):
        validator = ValidatorEnforceVocabulary(self.field)
        validator.field._vocabulary = ['L\xc3\xb2r\xc3\xa8m Ips\xc3\xb9m',
                                       'foo']
        self.assertEqual(str(validator.validate({'id': 'foo', 'label': 'Foo'},
                                                'bbb')),
                        'error_enforce_vocabulary')
        self.assertEqual(validator.validate({'id': 'foo', 'label': 'Foo'},
                                            'L\xc3\xb2r\xc3\xa8m Ips\xc3\xb9m'),
                         None)
