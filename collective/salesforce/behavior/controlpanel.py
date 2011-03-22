from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFPlone.interfaces import IPloneSiteRoot
from z3c.form import button
from z3c.form.form import Form
from plone.directives import form
from five import grok
from plone.autoform.form import AutoExtensibleForm
from collective.salesforce.behavior import _

class ISalesforceBehaviorControlPanel(form.Schema):
    """
    Schema for the Salesforce Behavior control panel.
    """
    
    form.widget(ftis='z3c.form.browser.checkbox.CheckBoxFieldWidget')
    ftis = schema.List(
        title=_(u'Types to Synchronize'),
        description=_(u'Select the content types to synchronize with Salesforce.'),
        value_type=schema.Choice(vocabulary='collective.salesforce.behavior.Types'),
        required=False,
    )

class SalesforceBehaviorControlPanelAdapter(grok.Adapter):
    """
    Adapts IPloneSiteRoot to ISalesforceBehaviorFormSchema.
    """
    
    grok.context(IPloneSiteRoot)
    grok.implements(ISalesforceBehaviorControlPanel)
    
    @property
    def ftis(self):
        """
        Select all available FTIs by default.
        """
        
        # Eventually we might want to store this persistently and use
        # it in syncs not triggered by the control panel.
        
        vocab = getUtility(IVocabularyFactory,
            name='collective.salesforce.behavior.Types')
        return [term.value for term in vocab(self.context)]

class SalesforceBehaviorControlPanel(AutoExtensibleForm, Form):
    """
    Control panel for performing actions related to Salesforce-integrated
    Dexterity types.
    """
    
    schema = ISalesforceBehaviorControlPanel
    label = _(u'Salesforce Behavior')
    ignore_context = True
    
    @button.buttonAndHandler(_(u'Synchronize Now'))
    def handleSync(self, action):
        data, errors = self.extractData()
        if errors:
            return
        ftis = data.get('ftis', [])
        if not ftis:
            self.status = _(u'Please select content types to synchronize.')
            return
        self.context.restrictedTraverse('@@sf_sync')(types=ftis)
        self.status = _(u'Salesforce synchronization successful.')
