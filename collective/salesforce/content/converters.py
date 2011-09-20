from zope.component import getAdapter
from zope.interface import implements
from plone.app.textfield.value import RichTextValue
from collective.salesforce.content.interfaces import ISalesforceValueConverter
        
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
            try: 
                return unicode(value, encoding='utf-8') 
            except TypeError: 
                # edge case for datetimes 
                return unicode(value)
        return None
        
class RichTextValueConverter(DefaultValueConverter):
    def toSchemaValue(self, value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """
    
        if value:
            return RichTextValue(unicode(value, 'utf-8'), 
                self.schema_field.default_mime_type,
                self.schema_field.output_mime_type)
        return None
        
class ListValueConverter(DefaultValueConverter):
    
    item_converter = u''

    def toSchemaValue(self, value):
        """
        Converts a Salesforce field value to a Zope schema value.
        """
        
        # Look up an item converter based on the value_type of the list
        # and use it to convert each of the list item values.
        item_converter = getAdapter(
            self.schema_field.value_type,
            interface=ISalesforceValueConverter,
            name=self.item_converter,
        )
        
        return [item_converter.toSchemaValue(item) for item in value]
