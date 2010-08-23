from setuptools import setup, find_packages

version = '0.1'

setup(name='collective.salesforce.behavior',
      version=version,
      description="Behaviors for creating Dexterity content types that integrate with Salesforce.",
      long_description=open("README.txt").read() + "\n" + open("CHANGES.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone Dexterity Salesforce behavior integration',
      author='Matt Yoder',
      author_email='mattyoder@groundwire.org',
      url='http://svn.plone.org/svn/collective/',
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
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
