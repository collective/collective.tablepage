# -*- coding: utf-8 -*-

PROJECTNAME = 'collective.tablepage'
RESERVED_IDS = ('__creator__', '__label__', '__cache__', 'id', '__uuid__',
                'getObjPositionInParent', 'SearchableText')

ADD_PERMISSIONS = {
    'TablePage': 'collective.tablepage: Add TablePage',
}
MANAGE_SEARCH_PERMISSION = "collective.tablepage: Access Search Configuration"

MANAGE_TABLE = "collective.tablepage: Manage Table"
MANAGE_LABEL = "collective.tablepage: Manage Label"

CATALOG_ID = 'tablepage_catalog'