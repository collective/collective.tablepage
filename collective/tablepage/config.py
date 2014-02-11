"""Common configuration constants
"""

PROJECTNAME = 'collective.tablepage'
RESERVED_IDS = ('__creator__', '__label__', '__cache__', 'id')
# Number of seconds the cache will be kept
CACHE_TIME = 3600

ADD_PERMISSIONS = {
    'TablePage': 'collective.tablepage: Add TablePage',
}

MANAGE_TABLE = "collective.tablepage: Manage Table"
MANAGE_LABEL = "collective.tablepage: Manage Label"