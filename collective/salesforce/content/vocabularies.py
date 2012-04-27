from operator import attrgetter
from zope.component import getAllUtilitiesRegisteredFor
from zope.annotation.interfaces import IAnnotations
from zope.site.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.dexterity.interfaces import IDexterityFTI
from five import grok
from collective.salesforce.content.interfaces import ISalesforceObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from BTrees.OOBTree import OOBTree


class TypesVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name('collective.salesforce.content.Types')

    def __call__(self, context):
        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        return SimpleVocabulary([SimpleTerm(fti.__name__, fti.__name__, fti.Title()) \
            for fti in ftis if ISalesforceObject.__identifier__ in fti.behaviors])


class PicklistsFromSalesforce(object):

    _data_key = 'collective.salesforce.content.picklists'

    _objects_to_get = {}
    
    def __init__(self, context):
        self.context = context
        
    @property
    def _data(self):
        ann = IAnnotations(self.context)
        data = ann.get(self._data_key, None)
        if data is None:
            ann[self._data_key] = data = OOBTree()
        return data
        
    def queryObjects(self):
        objects_to_get = self._objects_to_get
        if not objects_to_get:
            return

        site = getSite()
        if 'portal_salesforcebaseconnector' not in site:
            return []
        sfbc = getToolByName(site, 'portal_salesforcebaseconnector')
        
        # go through our list of SObjects, check if they have fields added,
        # and add them to our query
        sbj = []
        for o in objects_to_get.keys():
            if len(objects_to_get[o]['fields']):
                sbj.append(o)
                
        # if we have any objects to query run the query
        if len(sbj):
            sobjects = sfbc.describeSObjects(sbj)
            
            # check to make sure saleforce returned some objects
            if len(sobjects):
                
                #iterate over the returned SObjects and get the fields we want
                for sob in sobjects:
                    
                    name = sob.name
                    sf_fields = sob.fields
                    fields = objects_to_get[name]['fields']
                    
                    for f in fields:
                        
                        #make sure the sobject has the field we want
                        if f in sf_fields:
                            
                            terms = []
                            #iterate over the picklist values if any and create our term
                            for p in sf_fields[f].picklistValues:
                                value = safe_unicode(p['value'])
                                title = safe_unicode(p['label'])
                                token = title.encode('ascii', 'replace')
                                terms.append(SimpleTerm(value, token, title))
                                
                            #add the terms to our data cache
                            if len(terms):
                                data_key = name + '-' + f
                                
                                self._data[data_key] = []
                                self._data[data_key] = terms

    def _add_field(self, sobject, field):
        obs_to_get = self._objects_to_get
        
        if sobject not in obs_to_get:
            obs_to_get[sobject] = {'fields': []}
        
        if field not in obs_to_get[sobject]['fields']:
            obs_to_get[sobject]['fields'].append(field)
            
    def get_picklist_values(self, sobject, field):
        key = sobject + '-' + field
        terms = self._data.get(key, [])
        if terms:
            return terms
        
        self._add_field(sobject, field)
        self.queryObjects()
        
        terms = self._data.get(key, [])
        return terms


def get_picklist_from_sf(sobject, field):
    
    site = getSite()
    data_loader = PicklistsFromSalesforce(site)
    return sorted(data_loader.get_picklist_values(sobject, field), key=attrgetter('title'))
