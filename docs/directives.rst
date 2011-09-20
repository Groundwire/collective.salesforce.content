Directives
==========

The following directives may be used in XML schemas to configure
Salesforce-related functionality.

All the directives are in the ``http://namespaces.plone.org/salesforce/schema``
XML namespace. This namespace is usually configured at the top of the model
like so::

  <model xmlns="http://namespaces.plone.org/supermodel/schema"
         xmlns:sf="http://namespaces.plone.org/salesforce/schema">
    ...
  </model>

Schema directives
-----------------

These directives are valid as attributes of the ``schema`` tag.

``object``

  Indicates the Salesforce object type to which this schema corresponds.
  
  Example::
  
    <schema sf:object="Contact"></schema>

``container``

  Indicates the path to a folder where items synced using this schema should
  be created.
  
  If the folder does not yet exist at the time of sync, it will be created.

  Example::
  
    <schema sf:container="/contacts"></schema>

``criteria``

  Indicates additional criteria to limit which objects are retrieved from
  Salesforce.
  
  These criteria are added as a WHERE clause appended to the SOQL query passed
  to Salesforce.

  For example, the following schema definition::
  
    <schema sf:object="Contact" sf:criteria="Account.Name = 'Individual'"></schema>
    
  will be translated into the following SOQL query::
  
    SELECT Id FROM Contact WHERE Account.Name = 'Individual'


Field directives
----------------

These directives are valid as attributes of the ``field`` tag.

``field``

  Indicates the name of the corresponding field on the Salesforce object. The
  contents of the field will be mapped during a content sync.
  
  Example::
  
    <field name="first_name"
           type="zope.schema.TextLine"
           sf:field="FirstName"></field>
  
  This states that the ``first_name`` field in Plone corresponds to the
  ``FirstName`` field in Salesforce.
  
  A field may also be retrieved from a parent object. For example::
  
    <field name="org_name"
           type="zope.schema.TextLine"
           sf:field="Account.Name"></field>
  
  This states that the ``org_name`` field should be pulled from the name of the
  Contact's related Account.

``converter``

  Indicates the name of a custom converter that will be used to convert the
  value obtained from Salesforce into the value saved on the Plone object during
  sync. If no converter is specified, an attempt will be made to pick an
  appropriate one based on the field type.
  
  Example::
  
    <field name="is_active" type="zope.schema.Bool"
           sf:field="Active__c" sf:converter="string_to_bool"></field>
    
  In this example, the Active__c field in Salesforce contains either the string
  'true' or the string 'false', and we want to store a boolean in Plone.
  
  The implementation of the ``string_to_bool`` converter is as follows::
  
    from five import grok
    from zope.schema.interfaces import IBool
    from collective.salesforce.content.interfaces import ISalesforceValueConverter
    from collective.salesforce.content.converters import DefaultValueConverter
  
    class StringToBoolConverter(DefaultValueConverter, grok.Adapter):
        """ Should convert 'true' and 'false' into boolean values
        """
        grok.provides(ISalesforceValueConverter)
        grok.context(IBool)
        grok.name('string_to_bool')

        def toSchemaValue(self, value):
            if value:
                if value == 'true':
                    return True
                return False

``relationship``

  This is an advanced directive. Its main use is to allow a collection field
  (such as a List) to be populated with a series of objects from a Salesforce
  relationship.
  
  .. note::
     The related objects will be stored as attributes of the main content type
     being synced, so this approach is not appropriate when the related objects
     should be represented as full-fledged content items in their own right in
     Plone.
  
  Example: Say we want to save a list dictionaries on a Contact, one for each
  of the contact's campaign memberships. This could be done using the following
  field on the Contact schema::
  
    <field name="campaign_members" type="zope.schema.List"
           sf:relationship="CampaignMembers">
      <title>Campaign Memberships</title>
      <value_type type="collective.z3cform.datagridfield.DictRow">
        <schema>mypackage.interfaces.ICampaignMember</schema>
      </value_type>
    </field>
  
  In this example, ``mypackage.interfaces.ICampaignMember`` is a second schema based
  on the following model::
  
    <model xmlns="http://namespaces.plone.org/supermodel/schema"
           xmlns:sf="http://namespaces.plone.org/salesforce/schema">
      <schema sf:object="CampaignMember">
        <field name="title" type="zope.schema.TextLine"
               sf:field="Campaign.Name">
          <title>Campaign Name</title>
        </field>
        <field name="status" type="zope.schema.TextLine"
               sf:field="Status">
          <title>Campaign Status</title>
        </field>
      </schema>
    </model>

  After a sync, this would result in each Contact's ``campaign_members``
  attribute being set to a list of dictionaries, in the order returned by the
  Salesforce subquery. Each dictionary would have a ``name`` item and a
  ``status`` item.
  
  .. note::
     The subschema may have its own ``criteria`` directive to limit which
     related objects are queried.
  
  The ``relationship`` directive can also be used in conjunction with the
  ``field`` directive in order to obtain a single field from each of the
  related objects. For example, syncing the following field would set the
  ``campaigns`` attribute of each Contact to a set of the names of each
  Campaign of which the Contact is a member::
  
    <field name="campaign_member_ids" type="zope.schema.Set"
           sf:relationship="CampaignMembers" sf:field="Campaign.Name">
      <title>Campaigns</title>
    </field>

``subquery``

  This is an advanced directive. It allows the developer to inject an arbitrary
  subquery into the generated SOQL query to handle cases not supported by the
  other directives.
  
  Example::
  
    <schema sf:object="Contact">
      <field name="campaign_members"
             type="zope.schema.Set"
             sf:subquery="SELECT Id FROM CampaignMembers WHERE HasResponded=true"
             sf:converter="campaign_member_set"></field>
    </schema>
  
  would result in SOQL like::
  
    SELECT Id, (SELECT Id FROM CampaignMembers WHERE HasResponded=true) FROM Contact

  .. note::
     Notice the use of a custom converter via the ``converter`` directive. The
     ``subquery`` directive must always be used with a custom converter.
