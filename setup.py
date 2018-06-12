# -*- coding: utf-8 -*-

import os, sys
from setuptools import setup, find_packages

version = '1.0.0'

tests_require = ['plone.app.testing', 'pyquery', ]

install_requires = ['setuptools',
                    'Products.AdvancedQuery',
                    'collective.z3cform.datagridfield'
                    ]

setup(name='collective.tablepage',
      version=version,
      description="A Plone page with an editable table as main content",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone page table plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/collective.tablepage',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
