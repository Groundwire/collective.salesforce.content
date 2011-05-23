import unittest2 as unittest


class TestUtils(unittest.TestCase):
    
    def _makeSchema(self):
        from zope.interface import Interface
        from zope import schema

        class MySchema(Interface):
            title = schema.TextLine()

        return MySchema
    
    def test_queryFromSchema_no_tagged_values(self):
        schema = self._makeSchema()

        from collective.salesforce.behavior.utils import queryFromSchema
        query = queryFromSchema(schema)
        self.assertTrue(query is None)
    
    def test_queryFromSchema_object_criteria_fields(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'title': 'Name'})
        schema.setTaggedValue('salesforce.criteria', 'IsTest__c=true')
        
        from collective.salesforce.behavior.utils import queryFromSchema
        query = queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Name FROM Contact WHERE IsTest__c=true', query)
    
    def test_queryFromSchema_object_fields_no_criteria(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'title': 'Name'})
        
        from collective.salesforce.behavior.utils import queryFromSchema
        query = queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Name FROM Contact', query)
