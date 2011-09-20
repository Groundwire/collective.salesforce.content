How to...
=========

Set up automatic periodic synchronization
-----------------------------------------



Sync a single object on demand
------------------------------

Go to the Salesforce Content control panel in Site Setup.

In the `Salesforce object Id` box, enter the Id of the Salesforce object you
want to sync (you can obtain it from the URL when looking at the object in
Salesforce).  You must also select the content type corresponding to the
Salesforce object type of the item.

Click Synchronize Now to sync the single item.


Obtain the Salesforce Id of a Plone item
----------------------------------------

Use the behavior adapter::

  from collective.salesforce.content.interfaces import ISalesforceObject
  sf_object_id = ISalesforceObject(item).sf_object_id
  
This works as long as ``item`` is an item whose type has the ISalesforceObject
behavior enabled.


Retrieve a Plone item by Salesforce Id
--------------------------------------

Query the ``sf_object_id`` catalog index::

  from Products.CMFCore.utils import getToolByName
  catalog = getToolByName(context, 'portal_catalog')
  res = catalog.searchResults(sf_object_id=my_id)
  if res:
      item = res[0].getObject()


Perform custom actions when objects are synced, or no longer synced
-------------------------------------------------------------------

Two events may be raised for an object during sync:

.. autoclass:: collective.salesforce.content.events.NotFoundInSalesforceEvent

   There is an included, optional behavior which handles this event:

   .. autointerface:: collective.salesforce.content.interfaces.IPublishUpdated

.. autoclass:: collective.salesforce.content.events.UpdatedFromSalesforceEvent

   There are optional behaviors which handle this event:
   
   .. autointerface:: collective.salesforce.content.interfaces.IDeleteNotFound

   .. autointerface:: collective.salesforce.content.interfaces.IRejectNotFound

Sync objects in a particular order
----------------------------------

Since the ``criteria`` directive is added to the end of the generated SOQL query,
it can be abused to specify an ORDER BY clause. For example, this schema::

  <schema sf:object="Contact" sf:criteria="ORDER BY Name"></schema>
  
would result in the following SOQL::

  SELECT Id FROM Contact ORDER BY Name

There is not currently any mechanism to control the order in which multiple content
types using the ISalesforceObject behavior are synced, aside from triggering the
sync multiple times specifying different sets of content types.
