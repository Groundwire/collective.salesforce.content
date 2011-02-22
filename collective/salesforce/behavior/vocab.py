from time import time
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import directlyProvides
from plone.memoize import ram

@ram.cache(lambda *args: time() // 3600)
def list_sobject_types():
    sfbc = getToolByName(getSite(), 'portal_salesforcebaseconnector')
    return sfbc.describeGlobal()['types']

def SObjectTypesVocabularyFactory(context):
    types = list_sobject_types()
    return SimpleVocabulary.fromItems([(x, x) for x in types])
directlyProvides(SObjectTypesVocabularyFactory, IVocabularyFactory)

@ram.cache(lambda *args: (args, time() // 3600))
def list_sobject_fields(sf_obj_type):
    sfbc = getToolByName(getSite(), 'portal_salesforcebaseconnector')
    fields = sfbc.describeSObjects(sf_obj_type)[0].fields
    return sorted(fields.items(), key=lambda x: x[0])

def SObjectFieldsVocabularyFactory(context):
    sf_obj_type = getSite().REQUEST.form.get('form.widgets.sf_obj_type', ['Contact'])[0]
    if sf_obj_type is None:
        sf_obj_type = context.queryTaggedValue('salesforce.object', None)
        if sf_obj_type is None:
            return SimpleVocabulary([])
    
    terms = []
    for fname, fieldinfo in list_sobject_fields(sf_obj_type):
        if fname in ('Id', 'Name'):
            continue
        
        value = token = fname
        if fieldinfo.nillable or fieldinfo.defaultedOnCreate or not fieldinfo.createable:
            title = unicode(fname)
        else:
            title = u'%s (required)' % fname
        terms.append(SimpleTerm(value, token, title))
    return SimpleVocabulary(terms)
directlyProvides(SObjectFieldsVocabularyFactory, IVocabularyFactory)
