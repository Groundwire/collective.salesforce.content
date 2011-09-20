from zope import schema
from z3c.form import button
from z3c.form.form import Form
from plone.directives import form
from plone.autoform.form import AutoExtensibleForm
from collective.salesforce.content import _


class ISalesforceBehaviorControlPanel(form.Schema):
    """
    Schema for the Salesforce Behavior control panel.
    """
    
    form.widget(ftis='z3c.form.browser.checkbox.CheckBoxFieldWidget')
    ftis = schema.List(
        title=_(u'Types to Synchronize'),
        description=_(u'Select the content types to synchronize with Salesforce.'),
        value_type=schema.Choice(vocabulary='collective.salesforce.content.Types'),
        required = True,
    )
    
    sf_object_id = schema.ASCIILine(
        title = _(u'Salesforce object Id'),
        description = _(u'Optionally, specify a particular Salesforce object Id to synchronize. '
                        u'You must still specify the type of this object above.'),
        required = False,
        )


class SalesforceBehaviorControlPanel(AutoExtensibleForm, Form):
    """
    Control panel for performing actions related to Salesforce-integrated
    Dexterity types.
    """
    
    schema = ISalesforceBehaviorControlPanel
    label = _(u'Salesforce Content')
    ignoreContext = True
    
    @button.buttonAndHandler(_(u'Synchronize Now'))
    def handleSync(self, action):
        data, errors = self.extractData()
        if errors:
            return
        ftis = data.get('ftis', [])
        if not ftis:
            self.status = _(u'Please select content types to synchronize.')
            return
        self.context.restrictedTraverse('@@sf_sync')(types=ftis, sf_object_id=data['sf_object_id'])
        self.status = _(u'Salesforce synchronization successful.')
