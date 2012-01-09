from setuptools import setup, find_packages

version = '1.0'

setup(name='collective.salesforce.content',
      version=version,
      description="Behaviors for creating Dexterity content types that integrate with Salesforce.",
      long_description=open("README.rst").read() + "\n" + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Dexterity Salesforce behavior integration',
      author='Matt Yoder, Groundwire',
      author_email='mattyoder@groundwire.org',
      url='http://github.com/groundwire/collective.salesforce.content',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.salesforce'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.autopermission',
          'plone.app.dexterity',
          'plone.indexer',
          'Products.salesforcebaseconnector',
      ],
      extras_require={
          'test': ['plone.testing [zca]',],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
