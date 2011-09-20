import unittest2 as unittest


class TestDefaultValueConverter(unittest.TestCase):
    
    def _makeOne(self):
        from zope.schema import ASCIILine
        field = ASCIILine()
        
        from collective.salesforce.content.converters import DefaultValueConverter
        return DefaultValueConverter(field)
    
    def test_toSchemaValue(self):
        converter = self._makeOne()
        value = converter.toSchemaValue('foo')
        self.assertEquals('foo', value)
    
    def test_toSalesforceValue(self):
        converter = self._makeOne()
        _marker = object()
        value = converter.toSalesforceValue(_marker)
        self.assertTrue(value is _marker)


class TestTextLineValueConverter(unittest.TestCase):
    
    def _makeOne(self):
        from zope.schema import TextLine
        field = TextLine()
        
        from collective.salesforce.content.converters import TextLineValueConverter
        return TextLineValueConverter(field)
    
    def test_toSchemaValue(self):
        converter = self._makeOne()
        value = converter.toSchemaValue('foo')
        self.assertEquals(u'foo', value)

    def test_toSchemaValue_non_ascii(self):
        converter = self._makeOne()
        value = converter.toSchemaValue('\xe2\x80\x94')
        self.assertEquals(u'\u2014', value)
    
    def test_toSchemaValue_datetime(self):
        from datetime import datetime
        converter = self._makeOne()
        value = converter.toSchemaValue(datetime(2011, 1, 1))
        self.assertEquals(u'2011-01-01 00:00:00', value)

    def test_toSchemaValue_false(self):
        converter = self._makeOne()
        value = converter.toSchemaValue(False)
        self.assertTrue(value is None)


class TestRichTextValueConverter(unittest.TestCase):
    
    def _makeOne(self):
        from plone.app.textfield import RichText
        field = RichText()
        
        from collective.salesforce.content.converters import RichTextValueConverter
        return RichTextValueConverter(field)
    
    def test_toSchemaValue(self):
        converter = self._makeOne()
        value = converter.toSchemaValue('foo')
        self.assertEquals('foo', value.raw)

    def test_toSchemaValue_false(self):
        converter = self._makeOne()
        value = converter.toSchemaValue(False)
        self.assertTrue(value is None)
