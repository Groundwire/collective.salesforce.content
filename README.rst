Introduction
============

``collective.salesforce.content`` provides a Dexterity behavior for setting up
Plone Dexterity content types that are connected to objects in a Salesforce.com
database. These features are currently implemented:

* Metadata can be added to fields in a content type's schema to indicate how
  the Dexterity object maps to a Salesforce object.

* A Salesforce Object behavior that can be added to a Dexterity type. The
  behavior gives the type a Salesforce ID field and provides an indexer 
  for that field. It also acts as an adapter to the ISalesforeObject
  interface, which provides methods for syncing the object with Salesforce.

* A synchronization view that queries Salesforce and creates/updates the
  appropriate objects in Plone. It looks for Dexterity FTIs with the 
  aforementioned behavior, reads the Salesforce mappings from their schemas,
  and executes the appropriate queries.

* A simple converter system that uses adapters to convert values returned by
  Salesforce into the appropriate schema values and vice-versa. These
  converters can be registered globally for a particular field type, or they
  can be specified by name for a field instance.
  
These features remain to be completed:

* Recording changes from the Dexterity object back to Salesforce.

* Querying Salesforce for and updating a single Plone object.

* Converters for more complex field types.

Credits
=======

``collective.salesforce.content`` was created by the web team at `Groundwire`_,
including Matt Yoder, David Glick, Ryan Foster, and Jon Baldivieso.

.. _`Groundwire`: http://groundwire.org
