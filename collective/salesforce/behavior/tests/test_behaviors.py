import unittest2 as unittest


class DummyContent(object):
    pass


class TestSalesforceObject(unittest.TestCase):
    
    def _makeOne(self):
        from collective.salesforce.behavior.behaviors import SalesforceObject
        
        content_item = DummyContent()
        return SalesforceObject(content_item)
    
    def test_sf_object_id_setter(self):
        sfobj = self._makeOne()
        sfobj.sf_object_id = 'foo'
        self.assertEquals('foo', sfobj.context.sf_object_id)
    
    def test_sf_object_id_getter(self):
        sfobj = self._makeOne()
        sfobj.context.sf_object_id = 'foo'
        self.assertEquals('foo', sfobj.sf_object_id)


class TestMisc(unittest.TestCase):

    def test_sf_object_id_indexer(self):
        pass
        # needs a content item which can be adapted to ISalesforceObject,
        # probably needs the indexer adapter registered
