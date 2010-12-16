from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class ISalesforceBehaviorLayer(IDefaultBrowserLayer):
    """
    Browser layer for collective.salesforce.behavior.
    """

class ISalesforceObjectMarker(Interface):
    """
    Marker interface to indicate that this is a SalesForce object.
    """

class ISalesforceObject(Interface):
    """
    Behavior interface to make a type syncable with SalesForce.
    """
    
    sf_object_id = schema.ASCIILine(
        title=u'SalesForce Object ID',
    )
    
    def getSalesforceRecord():
        """
        Returns the record matching this object from Salesforce.
        """
            
    def updatePloneObject(record=None):
        """
        Given a record from Salesforce, update the corresponding Plone object.
        """
                    
    def getContainer(default=None):
        """
        Get the container object where new objects from Salesforce should
        be stored. Since the location can be specified using an instance method
        of the object, it is usually best to populate the object before
        attempting to get the container.
        """
        
    def addToContainer(container=None):
        """
        Adds the Plone object to the appropriate container.
        """
    
class ISalesforceValueConverter(Interface):
    """
    Converts values between Zope schema fields and Salesforce fields.
    """
    
    def toSchemaValue(value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """
        
    def toSalesforceValue(value):
        """
        Converts a Zope schema value to a Salesforce field value.
        """
        
class INotFoundInSalesforceEvent(IObjectEvent):
    """
    An object event that indicates that this object was not returned by
    Salesforce when its Dexterity type was synchronized.
    """
