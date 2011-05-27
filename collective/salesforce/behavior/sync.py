import transaction
import traceback
from zope.component import createObject, getUtility
from zope.event import notify
from zope.lifecycleevent import modified, ObjectCreatedEvent
from zope.publisher.browser import BrowserView
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from collective.salesforce.behavior import logger
from collective.salesforce.behavior.utils import queryFromSchema
from collective.salesforce.behavior.interfaces import ISalesforceObject, \
    ISalesforceObjectMarker
from collective.salesforce.behavior.events import NotFoundInSalesforceEvent, \
    UpdatedFromSalesforceEvent


class SFSync(BrowserView):
    """
    Synchronizes Plone objects with their corresponding Salesforce objects.
    """
    
    def __call__(self, catch_errors=False, email=None, types=[]):
        """
        Perform the synchronization.
        """
        
        try:
            logger.info('Syncing Salesforce objects for %s' 
                % self.context.Title())
            # Loop through the FTIs that include the ISalesforceObject behavior.
            for fti in self.getDexterityTypes():
                if types and not fti.__name__ in types:
                    continue
                if ISalesforceObject.__identifier__ in fti.behaviors:
                    query = self.getQueryFromType(fti)
                    logger.debug('SOQL: %s' % query)
                    if query:
                        results = self.getResults(query)
                        if results:
                            self.syncPloneObjects(fti, results)
        except:
            # If the catch_errors flag is set, we try to handle the error 
            # gracefully. This is mostly useful when using sf_sync
            # with Cron4Plone, which will try again if it gets an error.
            catch_errors = self.request.get('catch_errors', catch_errors)
            email = self.request.get('email', email)
            if catch_errors:
                message = traceback.format_exc()
                logger.error(message)
                if email:
                    # If we have an e-mail address, we try to send
                    # the traceback to that address.
                    MailHost = getToolByName(self.context, 'MailHost')
                    subject = u'Salesforce Sync Failure: %s' % self.context.Title()
                    sender = getUtility(ISiteRoot).email_from_address or email
                    try:
                        MailHost.secureSend(message, email, sender,
                            subject=subject, subtype='plain', charset='utf-8')
                    except:
                        pass
            else:
                raise
                        
    def getDexterityTypes(self):
        """
        Returns a list of Dexterity FTIs.
        """
        
        portal_types = getToolByName(self.context, 'portal_types')
        for fti in portal_types.listTypeInfo():
            if IDexterityFTI.providedBy(fti):
                yield fti
                        
    def getQueryFromType(self, fti):
        """
        Sync objects created from this FTI.
        """
        
        schema = fti.lookupSchema()
        return queryFromSchema(schema)
                                
    def getResults(self, query):
        """
        Get the results for this query from Salesforce.
        """
        
        sfbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
                
        results = sfbc.query(query)
        logger.debug('%s records found.' % results['size'])
        
        for result in results:
            yield result
        while not results['done']:
            results = sfbc.queryMore(results['queryLocator'])
            for result in results:
                yield result
        
    def syncPloneObjects(self, fti, records):
        """
        Given the results from Salesforce, update or create the appropriate
        Plone objects.
        """
        
        schema = fti.lookupSchema()
        
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'object_provides': {
                'query': [
                    schema.__identifier__,
                    ISalesforceObjectMarker.__identifier__,
                ],
                'operator': 'and',
            }
        }
        
        sfid_map = dict([(b.sf_object_id, b) for b in catalog.searchResults(query) \
            if b.sf_object_id])
        
        for i, record in enumerate(records):
            if record.Id in sfid_map.keys():
                sfobj = ISalesforceObject(sfid_map[record.Id].getObject())
                sfobj.updatePloneObject(record)
                del sfid_map[record.Id]
            else:
                obj = createObject(fti.factory)
                notify(ObjectCreatedEvent(obj))
                sfobj = ISalesforceObject(obj)
                sfobj.updatePloneObject(record)
                sfobj.addToContainer()
                
            # Reindex the object.
            modified(sfobj.context)
            
            # Send an UpdatedFromSalesforce event.
            notify(UpdatedFromSalesforceEvent(sfobj.context))
                                    
            # Commit periodically.
            if not i % 10:
                transaction.commit()
        
        # Send NotFoundInSalesforce events for objects that weren't
        # returned by the Salesforce query.
        for i, item in enumerate(sfid_map.items()):
            sf_id, brain = item
            notify(NotFoundInSalesforceEvent(brain.getObject()))
            
            # Commit periodically.
            if not i % 10:
                transaction.commit()
