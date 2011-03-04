from Acquisition import aq_base, aq_inner
from zope.app.content import queryContentType
from zope.app.component.hooks import getSite
from zope.app.container.interfaces import INameChooser
from zope.component import adapts, getAdapter
from zope.interface import implements
from zope.interface.interfaces import IInterface
from five import grok
from plone.indexer import indexer
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize import instance
from beatbox.python_client import QueryRecord
from collective.salesforce.behavior.interfaces import ISalesforceObject, \
    ISalesforceObjectMarker, ISalesforceValueConverter
from plone.app.dexterity.interfaces import IBehaviorActions
from plone.app.dexterity.interfaces import ITypeSchemaContext
from plone.app.dexterity.browser.behaviors import BehaviorAction
from Products.CMFCore.utils import getToolByName


class _marker(object):
    """
    Empty value marker.
    """

class SalesforceObject(object):
    implements(ISalesforceObject)
    adapts(IDexterityContent)
    
    def __init__(self, context):
        self.context = context
    
    def _get_sf_object_id(self):
        return getattr(self.context, 'sf_object_id', None)
        
    def _set_sf_object_id(self, sf_id):
        self.context.sf_object_id = sf_id
        
    sf_object_id = property(_get_sf_object_id, _set_sf_object_id)
    
    @instance.memoize
    def _getSchema(self):
        """
        Gets the schema for this content object. The schema must provide
        zope.app.content.interfaces.IContentType to be detected.
        """
        
        return queryContentType(self.context)
        
    def _queryTaggedValue(self, value, default=None):
        """
        Gets a tagged value from the schema.
        """
        
        schema = self._getSchema()
        if schema:
            return schema.queryTaggedValue(value, default)
        return default 
    
    def getSalesforceRecord(self):
        """
        Returns the record matching this object from Salesforce.
        """
        
        raise Exception('Not implemented.')
    
    def updatePloneObject(self, record=None):
        """
        Given a record from Salesforce, update the corresponding Plone object.
        """
        
        if not record:
            record = self.getSalesforceRecord()
        
        # Set the Salesforce ID from the record.
        if hasattr(record, 'Id'):
            self.sf_object_id = record.Id
        
        schema = self._getSchema()
        sf_fields = self._queryTaggedValue('salesforce.fields', {})
        sf_converters = self._queryTaggedValue('salesforce.converters', {})
                                
        for field in schema:
            if field in sf_fields.keys():
                
                # Try to get a corresponding value from the record.
                value = record
                for field_part in sf_fields[field].split('.'):
                    if type(value) == QueryRecord:
                        value = value.get(field_part, _marker)
                    else:
                        value = _marker
                        break
                
                # If we found a value, convert it to a schema value and
                # set it on the object.
                if not value is _marker:
                    converter_name = sf_converters.get(field, u'')
                    converter = getAdapter(
                        schema[field],
                        interface=ISalesforceValueConverter,
                        name=converter_name,
                    )
                    setattr(self.context, field, converter.toSchemaValue(value))
                    
    def getContainer(self, default=None):
        """
        Get the container object where new objects from Salesforce should
        be stored. Since the location can be specified using an instance method
        of the object, it is usually best to populate the object before
        attempting to get the container.
        """
        
        container_value = self._queryTaggedValue('salesforce.container', None)
        if not container_value:
            return default
        
        # First we see if this is an instance method of the object. If so,
        # it is responsible for returning the container object.
        container_factory = getattr(self.context, container_value, None)
        if callable(container_factory):
            return container_factory()
        
        # Otherwise, we assume this is a path relative to the site root
        # and attempt to traverse to it.
        if container_value.startswith('/'):
            container_value = container_value[1:]
        container = getSite().restrictedTraverse(container_value, None)
        if container:
            return container
        return default
        
    def addToContainer(self, container=None):
        """
        Adds the Plone object to the appropriate container.
        """
        
        if not container:
            container = self.getContainer()
            
        if not container:
            raise ValueError('Invalid container object.')
            
        container = aq_inner(container)
        name = INameChooser(container).chooseName(None, self.context)
        self.context.id = name
        
        new_name = container._setObject(name, self.context)
        self.context = container._getOb(new_name)


@indexer(ISalesforceObjectMarker)
def sf_object_id_indexer(obj):
    sfobj = ISalesforceObject(aq_base(obj), None)
    if sfobj:
        return sfobj.sf_object_id
    return None
grok.global_adapter(sf_object_id_indexer, name='sf_object_id')


def salesforce_behavior_actions(behavior_reg, context):
    if behavior_reg is ISalesforceObject and behavior_reg.__identifier__ in context.fti.behaviors:
        portal_url = getToolByName(context, 'portal_url')()
        return [
            BehaviorAction(title = 'Settings', href=context.absolute_url() + '/@@salesforce-settings'),
            BehaviorAction(title = 'Sync', href=portal_url + '/@@sf_sync'),
        ]
grok.global_adapter(salesforce_behavior_actions, (IInterface, ITypeSchemaContext), IBehaviorActions)
