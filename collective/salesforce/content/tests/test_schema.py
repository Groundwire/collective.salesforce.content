import unittest2 as unittest

from elementtree import ElementTree
from zope.interface import Interface
from zope import schema
from plone.supermodel.utils import ns
SF_NAMESPACE = "http://namespaces.plone.org/salesforce/schema"


class TestSalesforceObjectMetadata(unittest.TestCase):
    
    def _makeOne(self):
        from collective.salesforce.content.schema import SalesforceObjectMetadata
        return SalesforceObjectMetadata()

    def test_read(self):
        schema_node = ElementTree.Element('schema')
        schema_node.set(ns('object', SF_NAMESPACE), u'Orangutan')
        
        class IDummy(Interface):
            pass
        
        handler = self._makeOne()
        handler.read(schema_node, IDummy)
        
        self.assertEquals(u'Orangutan', IDummy.getTaggedValue('salesforce.object'))
    
    def test_write(self):
        schema_node = ElementTree.Element('schema')

        class IDummy(Interface):
            pass

        IDummy.setTaggedValue('salesforce.object', u'Chimpanzee')

        handler = self._makeOne()
        handler.write(schema_node, IDummy)

        self.assertEquals(u'Chimpanzee', schema_node.get(ns('object', SF_NAMESPACE)))


class TestSalesforceFieldMetadata(unittest.TestCase):

    def _makeOne(self):
        from collective.salesforce.content.schema import SalesforceFieldMetadata
        return SalesforceFieldMetadata()

    def test_read(self):
        schema_node = ElementTree.Element('schema')
        schema_node.set(ns('field', SF_NAMESPACE), u'Orangutan')

        class IDummy(Interface):
            foo = schema.TextLine()

        handler = self._makeOne()
        handler.read(schema_node, IDummy, IDummy['foo'])

        self.assertEquals({'foo': u'Orangutan'}, IDummy.getTaggedValue('salesforce.fields'))

    def test_write(self):
        schema_node = ElementTree.Element('schema')

        class IDummy(Interface):
            foo = schema.TextLine()

        IDummy.setTaggedValue('salesforce.fields', {'foo': u'Chimpanzee'})

        handler = self._makeOne()
        handler.write(schema_node, IDummy, IDummy['foo'])

        self.assertEquals('Chimpanzee', schema_node.get(ns('field', SF_NAMESPACE)))
