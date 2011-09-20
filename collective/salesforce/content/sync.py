import time
import transaction
import traceback
from zope.component import createObject, getUtility
from zope.interface import alsoProvides
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.publisher.browser import BrowserView
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from collective.salesforce.content import logger
from collective.salesforce.content.utils import queryFromSchema
from collective.salesforce.content.interfaces import ISalesforceObject
from collective.salesforce.content.interfaces import ISalesforceObjectMarker
from collective.salesforce.content.interfaces import IModifiedViaSalesforceSync
from collective.salesforce.content.events import NotFoundInSalesforceEvent, \
    UpdatedFromSalesforceEvent
from ZODB.POSException import ConflictError


try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1


class SFSync(BrowserView):
    """
    Synchronizes Plone objects with their corresponding Salesforce objects.
    """
    
    def __call__(self, catch_errors=False, email=None, types=[], sf_object_id=None):
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
                    query = self.getQueryFromType(fti, sf_object_id=sf_object_id)
                    logger.debug('SOQL: %s' % query)
                    if query:
                        results = self.getResults(query)
                        if results:
                            self.syncPloneObjects(fti, results, sf_object_id=sf_object_id)
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
                        
    def getQueryFromType(self, fti, sf_object_id=None):
        """
        Sync objects created from this FTI.
        """
        
        schema = fti.lookupSchema()
        return queryFromSchema(schema, sf_object_id=sf_object_id)
                                
    def getResults(self, query):
        """
        Get the results for this query from Salesforce.
        """
        
        sfbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
                
        results = sfbc.query(query)
        size = results['size']
        logger.debug('%s records found.' % size)
        
        for result in results:
            yield result
        while not results['done']:
            results = sfbc.queryMore(results['queryLocator'])
            logger.debug('Retrieved %s of %s records from Salesforce.' % (len(results), size))
            for result in results:
                yield result
        
    def syncPloneObjects(self, fti, records, sf_object_id=None):
        """
        Given the results from Salesforce, update or create the appropriate
        Plone objects.
        """
        
        time_start = time.time()
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
        
        objects_updated_count = 0
        for i, record in enumerate(records):
            digest = sha1(str(record)).digest()
            if record.Id in sfid_map.keys():
                sfobj = ISalesforceObject(sfid_map[record.Id].getObject())
                del sfid_map[record.Id]
            
                # skip updating items that haven't changed, based on the digest
                if digest == sfobj.sf_data_digest:
                    continue
            
                sfobj.updatePloneObject(record)
            else:
                obj = createObject(fti.factory)
                notify(ObjectCreatedEvent(obj))
                sfobj = ISalesforceObject(obj)
                sfobj.updatePloneObject(record)
                sfobj.addToContainer()
            
            objects_updated_count += 1
            sfobj.sf_data_digest = digest
            
            # Trigger ObjectModifiedEvent to reindex the object.
            # We mark it so that handlers can avoid taking action when
            # objects are updated in this way (such as a handler that
            # writes back to Salesforce).
            event = ObjectModifiedEvent(sfobj.context)
            alsoProvides(event, IModifiedViaSalesforceSync)
            notify(event)
            
            # Send an UpdatedFromSalesforce event.
            notify(UpdatedFromSalesforceEvent(sfobj.context))
                                    
            # Commit periodically.
            if not objects_updated_count % 10:
                try:
                    transaction.commit()
                    logger.debug('Committed updates (%s)' % i)
                except ConflictError:
                    # if there was a conflict subsequent commits will fail;
                    # so explicitly start a new transaction
                    logger.exception('Conflict on updates (%s)' % i)
                    transaction.begin()
        
        # Send NotFoundInSalesforce events for objects that weren't
        # returned by the Salesforce query.
        # We skip this if an sf_object_id was supplied, because that means
        # we intentionally didn't find all of the objects.
        if sf_object_id is None:
            for i, item in enumerate(sfid_map.items()):
                sf_id, brain = item
                notify(NotFoundInSalesforceEvent(brain.getObject()))
            
                # Commit periodically.
                if not i % 10:
                    transaction.commit()

        time_elapsed = time.time() - time_start
        logger.debug('Sync completed in %s seconds. Have a nice day.' % time_elapsed)
