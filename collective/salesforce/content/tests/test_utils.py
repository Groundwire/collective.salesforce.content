import unittest2 as unittest


class TestUtils(unittest.TestCase):
    
    def _makeSchema(self):
        from zope.interface import Interface
        from zope import schema

        class MySchema(Interface):
            scalar = schema.TextLine()
            vector = schema.List(
                value_type = schema.TextLine(),
                )

        return MySchema
    
    def _queryFromSchema(self, query):
        from collective.salesforce.content.utils import queryFromSchema
        return queryFromSchema(query)
    
    def test_queryFromSchema_no_tagged_values(self):
        schema = self._makeSchema()
        query = self._queryFromSchema(schema)
        self.assertTrue(query is None)

    def test_queryFromSchema_simple_field(self):
        # <field type="zope.schema.TextLine" sf:field="Name" />
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'scalar': 'Name'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Name FROM Contact', query)
        
    def test_queryFromSchema_duplicate_select(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'scalar': 'Name'})
        schema.setTaggedValue('salesforce.fields', {'vector': 'Name'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Name FROM Contact', query)

    def test_queryFromSchema_simple_field_with_criteria(self):
        # <field type="zope.schema.TextLine" sf:field="Name" sf:criteria="IsTest__c=true" />
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'scalar': 'Name'})
        schema.setTaggedValue('salesforce.criteria', 'IsTest__c=true')
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Name FROM Contact WHERE IsTest__c=true', query)

    def test_queryFromSchema_lookup_field(self):
        # <field type="zope.schema.TextLine" sf:field="Account.Name" />
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'scalar': 'Account.Name'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, Contact.Account.Name FROM Contact', query)

    def test_queryFromSchema_relationship_field(self):
        # <field type="zope.schema.List" sf:field="Name"
        #        sf:relationship="OpportunityContactRoles" />
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.fields', {'vector': 'Name'})
        schema.setTaggedValue('salesforce.relationships', {'vector': 'OpportunityContactRoles'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, (SELECT Name FROM Contact.OpportunityContactRoles) FROM Contact', query)

    def test_queryFromSchema_relationship_without_field(self):
        # Specifying a relationship with no fields is only supported if the
        # schema field is an IObjectField.
        # <field type="zope.schema.List" sf:relationship="OpportunityContactRoles" />
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.relationships', {'vector': 'OpportunityContactRoles'})
        self.assertRaises(ValueError, self._queryFromSchema, schema)

    def test_queryFromSchema_relationship_fields_to_list_of_objects(self):
        # main schema:
        # <schema sf:object="Contact">
        #   <field type="zope.schema.List" sf:relationship="OpportunityContactRoles">
        #     <value_type type="zope.schema.Object">
        #       <schema>path.to.ISubSchema</schema>
        #     </value_type>
        #   </field>
        # </schema>
        # 
        # subschema:
        # <schema sf:object="OpportunityContactRole" sf:criteria="Active__c=true">
        #   <field name="role" type="zope.schema.TextLine"
        #          sf:field="Role" />
        #   <field name="org" type="zope.schema.TextLine"
        #          sf:field="Account.Name" />
        # </schema>
        from zope.interface import Interface
        from zope import schema
        
        class subschema(Interface):
            role = schema.TextLine()
            org = schema.TextLine()
        
        class schema(Interface):
            opp_roles = schema.List(
                value_type = schema.Object(
                    schema = subschema
                    )
                )
        
        subschema.setTaggedValue('salesforce.object', 'OpportunityContactRole')
        subschema.setTaggedValue('salesforce.criteria', 'Active__c=true')
        subschema.setTaggedValue('salesforce.fields', {'role': 'Role', 'org': 'Account.Name'})
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.relationships', {'opp_roles': 'OpportunityContactRoles'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, (SELECT Id, Account.Name, Role FROM OpportunityContactRoles '
                         'WHERE Active__c=true) FROM Contact',
                         query)

    def test_queryFromSchema_custom_subquery(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.object', 'Contact')
        schema.setTaggedValue('salesforce.subqueries', {'scalar': '(SELECT foo FROM bar)'})
        query = self._queryFromSchema(schema)
        self.assertEqual('SELECT Contact.Id, (SELECT foo FROM bar) FROM Contact', query)
