# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig
from Products.CMFCore.utils import getToolByName

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

class TablePageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.tablepage
        xmlconfig.file('configure.zcml',
                       collective.tablepage,
                       context=configurationContext)
        z2.installProduct(app, 'collective.tablepage')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.tablepage:default')
        workflowTool = getToolByName(portal, 'portal_workflow')
        workflowTool.setDefaultChain('simple_publication_workflow')
        workflowTool.setChainForPortalTypes(('File',), ())
        #quickInstallProduct(portal, 'collective.analyticspanel')
        acl_users = getToolByName(portal, 'acl_users')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])
        acl_users.userFolderAddUser('user0', 'secret', ['Member', ], [])
        acl_users.userFolderAddUser('user1', 'secret', ['Member', 'Contributor'], [])
        acl_users.userFolderAddUser('user2', 'secret', ['Member', 'Contributor'], [])
        acl_users.userFolderAddUser('user3', 'secret', ['Member', 'Editor'], [])

TABLE_PAGE_FIXTURE = TablePageLayer()
TABLE_PAGE_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(TABLE_PAGE_FIXTURE, ),
                       name="TablePage:Integration")
TABLE_PAGE_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(TABLE_PAGE_FIXTURE, ),
                       name="TablePage:Functional")

