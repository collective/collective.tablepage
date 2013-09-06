# -*- coding: utf-8 -*-

import os, sys
from setuptools import setup, find_packages

version = '0.1'

tests_require = ['plone.app.testing', ]

install_requires = ['setuptools',
                    'Products.ATContentTypes',
                    'collective.datagridcolumns>0.4.0',
                    'Products.TinyMCE',
                    ]

if sys.version_info < (2, 6):
    # A RedTurtle branch (see https://github.com/RedTurtle/Products.DataGridField/tree/1.6)
    install_requires.append('Products.DatagridField>1.6.3')
else:
    install_requires.append('Products.DatagridField>=1.9.0dev')    

setup(name='collective.tablepage',
      version=version,
      description="A Plone content focused onto an editable table",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 3.3',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone page table plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://svn.plone.org/svn/collective/',
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
