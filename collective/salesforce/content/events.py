from zope.component.interfaces import ObjectEvent
from zope.interface import implements
from collective.salesforce.content.interfaces import \
    INotFoundInSalesforceEvent, IUpdatedFromSalesforceEvent

class NotFoundInSalesforceEvent(ObjectEvent):
    """
    An object event that indicates that this object was not returned by
    Salesforce when its Dexterity type was synchronized.
    """
    
    implements(INotFoundInSalesforceEvent)

class UpdatedFromSalesforceEvent(ObjectEvent):
    """
    An object event that indicates that this object was updated from Salesforce.
    """

    implements(IUpdatedFromSalesforceEvent)