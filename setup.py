import os
from setuptools import setup, find_packages

version = '2.0'

setup(name='Products.ATContentTypes',
      version=version,
      description="Default Content Types for Plone",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        ],
      keywords='Plone Content Types',
      author='AT Content Types development team',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.app.container',
            'zope.app.testing',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
          'setuptools',
          'plone.i18n',
          'plone.memoize',
          'plone.navigation',
          'plone.sequencebatch',
          'zope.annotation',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.publisher',
          'zope.tal',
          'Products.Archetypes',
          'Products.ATReferenceBrowserWidget',
          'Products.CMFCore',
          'Products.CMFDynamicViewFTI',
          'Products.CMFDefault',
          'Products.GenericSetup',
          'Products.MimetypesRegistry',
          'Products.PortalTransforms',
          'Products.validation',
          'Acquisition',
          'DateTime',
          'ExtensionClass',
          'transaction',
          'ZODB3',
          'Zope2',
      ],
      )
