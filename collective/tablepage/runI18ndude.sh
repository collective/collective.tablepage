#!/bin/sh

DOMAIN='collective.tablepage'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --keyword pmf --create ${DOMAIN} .
i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --merge locales/${DOMAIN}-manual.pot --create ${DOMAIN} .
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

#i18ndude rebuild-pot --pot i18n/${DOMAIN}-plone.pot --create plone .
i18ndude sync --pot i18n/${DOMAIN}-plone.pot i18n/${DOMAIN}-plone-??.po
