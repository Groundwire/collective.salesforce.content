from zope.component import getAllUtilitiesRegisteredFor
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.dexterity.interfaces import IDexterityFTI
from five import grok
from collective.salesforce.content.interfaces import ISalesforceObject

class TypesVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name('collective.salesforce.content.Types')

    def __call__(self, context):
        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        return SimpleVocabulary([SimpleTerm(fti.__name__, fti.__name__, fti.Title()) \
            for fti in ftis if ISalesforceObject.__identifier__ in fti.behaviors])