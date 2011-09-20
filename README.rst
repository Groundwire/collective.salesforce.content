Introduction
============

collective.salesforce.content provides a behavior and related tools for
creating Salesforce-enabled Dexterity content types. These features are
currently implemented:

* A set of Salesforce metadata attributes that can be included in a Dexterity
  schema. These attributes describe how the Dexterity object maps to a
  Salesforce object.

* A Salesforce Object behavior that can be added to a Dexterity type. The
  behavior gives the type a Salesforce ID field and provides an indexer 
  for that field. It also acts as an adapter to the ISalesforeObject
  interface, which provides methods for syncing the object with Salesforce.

* A synchronization view that queries Salesforce and creates/updates the
  appropriate objects in Plone. It looks for Dexterity FTIs with the 
  aforementioned behavior, reads the Salesforce mappings from their schemas,
  and executes the appropriate queries.  It also includes some error handling
  so that it can be used with Cron4Plone.

* A simple converter system that uses adapters to convert values returned by
  Salesforce into the appropriate schema values and vice-versa. These
  converters can be registered globally for a particular field type, or they
  can be specified by name for a field instance.
  
These features remain to be completed:

* Pushing values from the Dexterity object back to Salesforce.

* Querying Salesforce for and updating a single Plone object.

* Converters for more complex field types.

* Support for Object fields and subqueries.

* Tests and documentation.