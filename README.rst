Introduction
============

``collective.salesforce.content`` provides a Dexterity behavior for setting up
Plone Dexterity content types that are connected to objects in a Salesforce.com
database. Arbitrary schema fields can be mapped and updated periodically based on
automatic queries to Salesforce.

This is currently an integrator-level package with minimal UI. As consultants,
we have used this functionality as a foundation for solving use cases like:

* Expose a member directory on a public Plone website based on Account or Contact
  records pulled from Salesforce.com each night.

* Provide browseable and searchable tables of arbitrary data whose
  canonical storage is in Salesforce.com.

* In conjunction with ``dexterity.membrane``, allow users represented in
  Salesforce.com to log in to a Plone site, with appropriate roles based on their
  status in Salesforce.com.

* Pull pricing records from Salesforce as a basis for charging the correct amount
  in online transactions on the Plone website.

Documentation
=============

`Read the documentation <http://readthedocs.org/docs/collectivesalesforcecontent/en/latest/>`_.

Issue Tracker
=============

`Submit issues <https://github.com/Groundwire/collective.salesforce.content/issues>`_.

Credits
=======

``collective.salesforce.content`` was created by the web team at `Groundwire`_,
including Matt Yoder, David Glick, Ryan Foster, and Jon Baldivieso.

.. _`Groundwire`: http://groundwire.org
