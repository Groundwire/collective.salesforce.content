# upgrade step to replace collective.salesforce.behavior
# with collective.salesforce.content

from plone.browserlayer.utils import unregister_layer
from Products.CMFCore.utils import getToolByName

_marker = object()


def replace_c_s_behavior(context):
    qi = getToolByName(context, 'portal_quickinstaller')

    # remove old browser layer
    try:
        unregister_layer('collective.salesforce.behavior')
    except KeyError:
        pass

    # remove old configlet
    cp = getToolByName(context, 'portal_controlpanel')
    cp.unregisterConfiglet('collective.salesforce.behavior')

    # update behavior locations in existing types
    ttool = getToolByName(context, 'portal_types')
    for fti in ttool.objectValues():
        if getattr(fti, 'behaviors', _marker) is not _marker:
            fti.behaviors = [b.replace('collective.salesforce.behavior',
                                       'collective.salesforce.content')
                             for b in fti.behaviors]

    # remove record of c.s.behavior being installed
    if 'collective.salesforce.behavior' in qi:
        qi.manage_delObjects(['collective.salesforce.behavior'])

    # make sure new package is installed
    if not qi.isProductInstalled('collective.salesforce.content'):
        qi.installProducts(['collective.salesforce.content'])
