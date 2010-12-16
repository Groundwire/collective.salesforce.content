from zope.interface import implements
from plone.app.textfield.value import RichTextValue
from collective.salesforce.behavior.interfaces import ISalesforceValueConverter
        
class DefaultValueConverter(object):
    implements(ISalesforceValueConverter)
    
    def __init__(self, schema_field):
        self.schema_field = schema_field
        
    def toSchemaValue(self, value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """
        
        return value

    def toSalesforceValue(self, value):
        """
        Converts a Zope schema value to a Salesforce field value.
        """
        
        return value
        
class TextLineValueConverter(DefaultValueConverter):
    
    def toSchemaValue(self, value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """
        
        if value:
            return unicode(value, encoding='utf-8')
        return None
        
class RichTextValueConverter(DefaultValueConverter):

    def toSchemaValue(self, value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """

        if value:
            return RichTextValue(value, 'text/plain',
                self.schema_field.output_mime_type)
        return None