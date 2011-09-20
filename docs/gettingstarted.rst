Getting Started
===============

Although it may someday become a product that can be used through the web,
``collective.salesforce.content`` is currently an integrator tool, which
requires creating a Plone add-on package.

1. `Install Dexterity <http://plone.org/products/dexterity/documentation/how-to/install>`_.

2. `Create a new Plone add-on using ZopeSkel <http://plone.org/products/dexterity/documentation/manual/developer-manual/pre-requisites/creating-a-package>`_.

3. Add ``collective.salesforce.content`` as a dependency of your add-on.

   Add it to ``install_requires`` in setup.py::
    
    install_requires=[
        'collective.salesforce.content',
        ...
        ],
  
   And add its GenericSetup profile as a dependency of your own in 
   profiles/default/metadata.xml::
   
    <?xml version="1.0"?>
    <metadata>
      <version>1</version>
      <dependencies>
        <dependency>profile-collective.salesforce.content:default</dependency>
      </dependencies>
    </metadata>

4. Add a new Dexterity content type to the package. For example, to add a
   "Contact" content type, do the following:
   
   a. Add ``profiles/default/types/Contact.xml``::
   
        <?xml version="1.0"?>
        <object name="Contact" meta_type="Dexterity FTI"
           xmlns:i18n="http://xml.zope.org/namespaces/i18n">
         <property name="title">Contact</property>
         <property name="description">A Salesforce Contact.</property>
         <property name="icon_expr">string:${portal_url}/user.png</property>
         <property name="link_target"></property>
         <property name="immediate_view">view</property>
         <property name="global_allow">False</property>
         <property name="filter_content_types">True</property>
         <property name="allowed_content_types"/>
         <property name="allow_discussion">False</property>
         <property name="default_view">view</property>
         <property name="view_methods">
          <element value="view"/>
         </property>
         <property name="default_view_fallback">False</property>
         <property name="klass">plone.dexterity.content.Item</property>
         <property name="behaviors">
           <element value="collective.salesforce.content.interfaces.ISalesforceObject"/>
         </property>
         <property name="model_file">mypackage:models/Contact.xml</property>
         <alias from="(Default)" to="(dynamic view)"/>
         <alias from="edit" to="@@edit"/>
         <alias from="sharing" to="@@sharing"/>
         <alias from="view" to="(selected layout)"/>
         <action title="View" action_id="view" category="object" condition_expr=""
            icon_expr="" link_target="" url_expr="string:${object_url}"
            visible="True">
          <permission value="View"/>
         </action>
         <action title="Edit" action_id="edit" category="object" condition_expr=""
            icon_expr="" link_target="" url_expr="string:${object_url}/edit"
            visible="True">
          <permission value="Modify portal content"/>
         </action>
        </object>
      
      Notice that we enabled the ``ISalesforceObject`` behavior.
      
      .. note::
      
         Be sure to replace ``mypackage`` with the name of your add-on package.
      
  b. Add the type to ``profiles/default/types.xml``::
  
       <?xml version="1.0"?>
       <object meta_type="Plone Types Tool" name="portal_types">
        <object meta_type="Dexterity FTI" name="Contact" />
       </object>
  
  c. Add ``models/Contact.xml`` with the type's schema::
  
       <model xmlns="http://namespaces.plone.org/supermodel/schema"
              xmlns:sf="http://namespaces.plone.org/salesforce/schema">
         <schema sf:object="Contact" sf:container="/contacts">
           <field name="title" type="zope.schema.TextLine" sf:field="Name">
             <title>Name</title>
           </field>
         </schema>
       </model>
     
     This is a very basic schema including some 
     ``collective.salesforce.content`` annotations to state that:
     
     * This content type corresponds to the Contact object type in Salesforce 
       (sf:object).
     * During a sync, Contacts should be added within the "/contacts" folder.
       (sf:container)
     * The `title` field should be populated from the `Name` field in 
       Salesforce.
     
     .. note::

        See the Dexterity documentation for more information on writing schemas

        Dexterity schemas can also be specified in the form of a Zope schema in
        Python. However, the schema directives provided by 
        ``collective.salesforce.content`` are currently only available for XML 
        schemas.

4. Start up Plone, go to ``portal_salesforcebaseconnector`` in the ZMI, and
   configure your Salesforce credentials.

5. Go to the Add-ons control panel in Site Setup, and install your add-on.

6. Go to the Salesforce Content control panel, select your content type, and 
   click the ``Synchronise now`` button.
   
   .. note::
   
      This may take some time if your Salesforce instance has a lot of objects.

   When finished, the content should now exist in its container in Plone. In our
   example, the /contacts folder should be filled with Contacts.
