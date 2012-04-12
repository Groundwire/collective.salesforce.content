from zope.schema._field import Choice, Set
from zope.schema.vocabulary import SimpleVocabulary
from .vocabularies import get_picklist_from_sf
from plone.supermodel.exportimport import BaseHandler


class SalesforcePicklist(Choice):

    def __init__(self, **kw):
        self.vocabulary = None
        if 'parent' in kw:
            self.parent = kw.pop('parent')
        self._init_field = True
        super(Choice, self).__init__(**kw)
        self._init_field = False

    def bind(self, object):
        clone = super(Choice, self).bind(object)
        if hasattr(clone, 'parent'):
            interface = clone.parent.interface
            fieldname = clone.parent.__name__
            # avoid circular reference
            clone.parent = None
        else:
            interface = clone.interface
            fieldname = clone.__name__
        objectname = interface.getTaggedValue('salesforce.object')
        fieldname = interface.getTaggedValue('salesforce.fields').get(fieldname)
        terms = get_picklist_from_sf(objectname, fieldname)
        clone.vocabulary = SimpleVocabulary(terms)
        return clone


class SalesforceMultiPicklist(Set):

    def __init__(self, **kw):
        kw['value_type'] = SalesforcePicklist(parent=self)
        super(SalesforceMultiPicklist, self).__init__(**kw)


SalesforcePicklistHandler = BaseHandler(SalesforcePicklist)
SalesforceMultiPicklistHandler = BaseHandler(SalesforceMultiPicklist)
