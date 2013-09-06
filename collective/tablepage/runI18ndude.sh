#!/bin/sh

DOMAIN='collective.tablepage'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} .
i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --merge locales/${DOMAIN}-manual.pot --create ${DOMAIN} .
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

