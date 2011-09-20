import unittest2 as unittest
from zope.component import provideAdapter
from zope.interface import Interface, implements, directlyProvides
from zope import schema
from zope.app.content.interfaces import IContentType
from plone.testing.zca import UNIT_TESTING


class TestSalesforceObject(unittest.TestCase):
    layer = UNIT_TESTING
    
    def _makeSite(self, expected_container):
        from zope.site.site import SiteManagerContainer
        from zope.site.testing import siteSetUp, createSiteManager
        class DummySite(SiteManagerContainer):
            def restrictedTraverse(*args):
                return expected_container
        siteSetUp()
        site = DummySite()
        createSiteManager(site, setsite=True)
        return site
    
    def _makeSchema(self):
        class IDummySchema(Interface):
            pass
        directlyProvides(IDummySchema, IContentType)
        return IDummySchema
    
    def _makeOne(self, context=None, schema=None):
        if schema is None:
            schema = self._makeSchema()
        
        if context is None:
            class DummyContent(object):
                implements(schema)
            context = DummyContent()
        
        from collective.salesforce.content.behaviors import SalesforceObject
        return SalesforceObject(context)
    
    def test_sf_object_id_setter(self):
        sfobj = self._makeOne()
        sfobj.sf_object_id = 'foo'
        self.assertEquals('foo', sfobj.context.sf_object_id)
    
    def test_sf_object_id_getter(self):
        sfobj = self._makeOne()
        sfobj.context.sf_object_id = 'foo'
        self.assertEquals('foo', sfobj.sf_object_id)

    def test__getSchema(self):
        schema = self._makeSchema()
        sfobj = self._makeOne(schema = schema)
        self.failUnless(sfobj._getSchema() is schema)
    
    def test__queryTaggedValue(self):
        schema = self._makeSchema()
        schema.setTaggedValue('foo', 'bar')        
        sfobj = self._makeOne(schema = schema)
        self.assertEqual('bar', sfobj._queryTaggedValue('foo'))
    
    def test__queryTaggedValue_no_schema(self):
        class DummyContent(object):
            pass
        sfobj = self._makeOne(DummyContent())
        self.assertTrue(sfobj._queryTaggedValue('foo') is None)
    
    def test_getSalesforceRecord(self):
        sfobj = self._makeOne()
        self.assertRaises(Exception, sfobj.getSalesforceRecord)
    
    def test_updatePloneObject_simple_fields(self):
        from collective.salesforce.content.converters import TextLineValueConverter
        from zope.schema.interfaces import ITextLine
        provideAdapter(TextLineValueConverter, [ITextLine])
        
        class IDummySchema(Interface):
            title = schema.TextLine()
            foo = schema.TextLine()
        directlyProvides(IDummySchema, IContentType)
        IDummySchema.setTaggedValue('salesforce.fields', {'title': 'Name', 'foo': 'Name.bar'})
        sfobj = self._makeOne(schema = IDummySchema)
        
        from beatbox.python_client import QueryRecord
        record = QueryRecord(
            Id = '1234',
            Name = 'Dracula',
            )
        
        sfobj.updatePloneObject(record=record)
        self.assertEqual('1234', sfobj.sf_object_id)
        self.assertEqual(u'Dracula', sfobj.context.title)
    
    def test_updatePloneObject_lookup_field(self):
        from collective.salesforce.content.converters import TextLineValueConverter
        provideAdapter(TextLineValueConverter, [schema.interfaces.ITextLine])
        
        class IDummySchema(Interface):
            title = schema.TextLine()
        directlyProvides(IDummySchema, IContentType)
        IDummySchema.setTaggedValue('salesforce.fields', {'title': 'Account.Name'})
        sfobj = self._makeOne(schema = IDummySchema)
        
        from beatbox.python_client import QueryRecord
        record = QueryRecord(
            Id = '1234',
            Account = QueryRecord(
                Name = 'Hogwarts',
                ),
            )
        
        sfobj.updatePloneObject(record=record)
        self.assertEqual(u'Hogwarts', sfobj.context.title)
    
    def test_updatePloneObject_relationship_field(self):
        from collective.salesforce.content.converters import TextLineValueConverter
        provideAdapter(TextLineValueConverter, [schema.interfaces.ITextLine])
        from collective.salesforce.content.converters import ListValueConverter
        provideAdapter(ListValueConverter, [schema.interfaces.IList])
        
        class IDummySchema(Interface):
            roles = schema.List(value_type=schema.TextLine())
        directlyProvides(IDummySchema, IContentType)
        IDummySchema.setTaggedValue('salesforce.fields', {'roles': 'Role'})
        IDummySchema.setTaggedValue('salesforce.relationships', {'roles': 'OpportunityContactRoles'})
        sfobj = self._makeOne(schema = IDummySchema)
        
        from beatbox.python_client import QueryRecord, QueryRecordSet
        record = QueryRecord(
            Id = '1234',
            OpportunityContactRoles = QueryRecordSet(
                records = [QueryRecord(
                    Role = 'Terminator',
                    )],
                done = True,
                size = 1,
                )
            )
        
        sfobj.updatePloneObject(record=record)
        self.assertEqual([u'Terminator'], sfobj.context.roles)
    
    def test_updatePloneObject_relationship_fields_to_list_of_objects(self):
        from collective.salesforce.content.converters import TextLineValueConverter
        provideAdapter(TextLineValueConverter, [schema.interfaces.ITextLine])
        from collective.salesforce.content.converters import ListValueConverter
        provideAdapter(ListValueConverter, [schema.interfaces.IList])
        
        class IDummyOppRoleSchema(Interface):
            role = schema.TextLine()
            org = schema.TextLine()
        IDummyOppRoleSchema.setTaggedValue('salesforce.object', 'OpportunityRole')
        IDummyOppRoleSchema.setTaggedValue('salesforce.fields', {'role': 'Role', 'org': 'Account.Name'})
        class IDummyContactSchema(Interface):
            roles = schema.List(value_type=schema.Object(schema=IDummyOppRoleSchema))
        directlyProvides(IDummyContactSchema, IContentType)
        IDummyContactSchema.setTaggedValue('salesforce.relationships', {'roles': 'OpportunityContactRoles'})
        sfobj = self._makeOne(schema = IDummyContactSchema)
        
        from beatbox.python_client import QueryRecord, QueryRecordSet
        record = QueryRecord(
            Id = '1234',
            OpportunityContactRoles = QueryRecordSet(
                records = [QueryRecord(
                    Role = 'Code Monkey',
                    Account = QueryRecord(
                        Name = 'Groundwire',
                        ),
                    )],
                done = True,
                size = 1,
                )
            )
        
        sfobj.updatePloneObject(record=record)
        self.assertEqual([{'org': u'Groundwire', 'role': u'Code Monkey'}], sfobj.context.roles)
    
    def test_updatePloneObject_no_record(self):
        sfobj = self._makeOne()
        self.assertRaises(Exception, sfobj.updatePloneObject)
    
    def test_getContainer(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.container', 'foo')
        sfobj = self._makeOne(schema = schema)
        expected_container = object()
        self._makeSite(expected_container)

        container = sfobj.getContainer()
        self.assertTrue(container is expected_container)
    
    def test_getContainer_leading_slash(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.container', '/foo')
        sfobj = self._makeOne(schema = schema)
        expected_container = object()
        self._makeSite(expected_container)

        container = sfobj.getContainer()
        self.assertTrue(container is expected_container)

    def test_getContainer_no_container_set(self):
        sfobj = self._makeOne()
        _marker = object()
        container = sfobj.getContainer(default=_marker)
        self.assertTrue(container is _marker)
    
    def test_getContainer_value_is_callable(self):
        schema = self._makeSchema()
        expected_container = object()
        class DummyContent(object):
            implements(schema)
            
            def getContainer(self):
                return expected_container
        schema.setTaggedValue('salesforce.container', 'getContainer')
        sfobj = self._makeOne(context=DummyContent())
        
        container = sfobj.getContainer()
        self.assertTrue(container is expected_container)
    
    def test_getContainer_not_found(self):
        schema = self._makeSchema()
        schema.setTaggedValue('salesforce.container', 'foo')
        sfobj = self._makeOne(schema = schema)
        expected_container = object()
        self._makeSite(expected_container = None)

        container = sfobj.getContainer(default=expected_container)
        self.assertTrue(container is expected_container)
        

class TestMisc(unittest.TestCase):

    def test_sf_object_id_indexer(self):
        pass
        # needs a content item which can be adapted to ISalesforceObject,
        # probably needs the indexer adapter registered
