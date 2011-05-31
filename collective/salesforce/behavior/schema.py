from zope.interface import implements
from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import IFieldMetadataHandler
from plone.supermodel.utils import ns

SF_NAMESPACE = "http://namespaces.plone.org/salesforce/schema"
SF_PREFIX = "sf"

class BaseSalesforceMetadata(object):
    implements(ISchemaMetadataHandler)
    
    namespace = SF_NAMESPACE
    prefix = SF_PREFIX
    
    def read(self, schemaNode, schema):
        value = schemaNode.get(ns(self.xml_attr, self.namespace))
        if value:
            schema.setTaggedValue(self.tag_key, value)
            
    def write(self, schemaNode, schema):
        value = schema.queryTaggedValue(self.tag_key, None)
        if value:
            schemaNode.set(ns(self.xml_attr, self.namespace), value)

class BaseSalesforceFieldMetadata(object):
    implements(IFieldMetadataHandler)

    namespace = SF_NAMESPACE
    prefix = SF_PREFIX

    def read(self, fieldNode, schema, field):
        name = field.__name__
        value = fieldNode.get(ns(self.xml_attr, self.namespace))
        if value:
            values = schema.queryTaggedValue(self.tag_key, {})
            values[name] = value
            schema.setTaggedValue(self.tag_key, values)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        value = schema.queryTaggedValue(self.tag_key, {}).get(name, {})
        if value:
            fieldNode.set(ns(self.xml_attr, self.namespace), value)

class SalesforceObjectMetadata(BaseSalesforceMetadata):
    xml_attr = 'object'
    tag_key = 'salesforce.object'

class SalesforceCriteriaMetadata(BaseSalesforceMetadata):
    xml_attr = 'criteria'
    tag_key = 'salesforce.criteria'

class SalesforceContainerMetadata(BaseSalesforceMetadata):
    xml_attr = 'container'
    tag_key = 'salesforce.container'

class SalesforceFieldMetadata(BaseSalesforceFieldMetadata):
    xml_attr = 'field'
    tag_key = 'salesforce.fields'
    
class SalesforceRelationshipMetadata(BaseSalesforceFieldMetadata):
    xml_attr = 'relationship'
    tag_key = 'salesforce.relationships'

class SalesforceSubqueryMetadata(BaseSalesforceFieldMetadata):
    xml_attr = 'subquery'
    tag_key = 'salesforce.subqueries'

class SalesforceConverterMetadata(BaseSalesforceFieldMetadata):
    xml_attr = 'converter'
    tag_key = 'salesforce.converters'