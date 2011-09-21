How to...
=========

Set up automatic periodic synchronization
-----------------------------------------

Here is one way to automatically trigger the sync via a cron job. The sync will
run in a separate process from your standard backend instances, so you must be
using ZEO or RelStorage to allow multiple database connections.

1. In the root of your buildout, create a file ``cronviews.py.in``::

    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl.SecurityManager import setSecurityPolicy
    from Testing.makerequest import makerequest
    from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
    from zope.app.publication.interfaces import BeforeTraverseEvent
    from zope.event import notify
    import transaction

    # Get our variables from buildout in order.
    site_path = '${site-path}'
    view_names = """${views}"""

    site_path = site_path.strip().strip('/')
    views = [v.strip() for v in view_names.split() if v.strip()]

    # Set up a generic manager user.
    _policy=PermissiveSecurityPolicy()
    _oldpolicy=setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

    # Set a request so that traversal succeeds.
    app = makerequest(app)

    # Fire a before traversal event so that browser layers get applied.
    site = app.restrictedTraverse(site_path)
    notify(BeforeTraverseEvent(site, site.REQUEST))

    # Try to open the views.
    for view in views:
        try:
            site.restrictedTraverse(view)()
            transaction.commit()
        except:
            import traceback
            traceback.print_exc()

2. Add sections to buildout.cfg to install this script and run it via cron
   (be sure to replace ``path/to/site``)::

    [buildout]
    parts =
        cronviews
        sfsync

    [cronviews]
    recipe = collective.recipe.template
    input = ${buildout:directory}/cronviews.py.in
    output = ${buildout:directory}/etc/cronviews.py
    site-path = path/to/site
    views =  
        @@sf_sync
    
    [sfsync]
    recipe = z3c.recipe.usercrontab
    times = 00 1 * * *
    command = ${buildout:executable} ${buildout:bin-directory}/instance run ${buildout:directory}/etc/cronviews.py

3. Run the buildout to install the cron job.

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

``collective.salesforce.content.events.NotFoundInSalesforceEvent``

  An object event that indicates that this object was not returned by
  Salesforce when its Dexterity type was synchronized.

  There is an included, optional behavior which handles this event:

  ``collective.salesforce.content.interfaces.IPublishUpdated``
    Causes an object to be published after it is updated from Salesforce during a sync.

``collective.salesforce.content.events.UpdatedFromSalesforceEvent``

  An object event that indicates that this object was updated from Salesforce.
  
  There are optional behaviors which handle this event:
   
  ``collective.salesforce.content.interfaces.IDeleteNotFound``
    Causes an item with this behavior to be deleted from Plone if it is not
    found during a Salesforce sync.

  ``collective.salesforce.content.interfaces.IRejectNotFound``
    Causes an item to be rejected (in the workflow sense, i.e. made private) if
    it is not found during a Salesforce sync.

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
