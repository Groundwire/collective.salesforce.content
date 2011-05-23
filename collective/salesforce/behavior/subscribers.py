from Products.CMFCore.utils import getToolByName
from five import grok
from collective.salesforce.behavior.interfaces import \
    IUpdatedFromSalesforceEvent, INotFoundInSalesforceEvent, \
    IPublishUpdated, IRejectNotFound
    
def _transitionIfAvailable(transition, obj):
    """
    Invoke the specified transition if it is available for the object.
    """
    
    portal_workflow = getToolByName(obj, 'portal_workflow')
    transitions = [t['id'] for t in portal_workflow.getTransitionsFor(obj)]
    if transition in transitions:
        portal_workflow.doActionFor(obj, transition)

@grok.subscribe(IPublishUpdated, IUpdatedFromSalesforceEvent)
def publishUpdatedObjects(obj, event):
    """
    Publish an object after it has been updated from Salesforce.
    """

    _transitionIfAvailable('publish', obj)

@grok.subscribe(IRejectNotFound, INotFoundInSalesforceEvent)
def rejectNotFoundObjects(obj, event):
    """
    Reject an object if it is not found in Salesforce.
    """

    _transitionIfAvailable('reject', obj)
