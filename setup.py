#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='python_wordpress_utils',
      version='0.5',
      description='WordPress XML-RPC Utilties ',
      author='Joe VanAndel ',
      author_email='joe.vanandel@mgmail.com',
      url='https://github.com/vanandel/python-wordpress-utils/',
      packages=['wordpress_utils', ],
      license='MIT',
      test_suite='nose.collector',
      classifiers=[
          'Programming Language :: Python',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Internet :: WWW/HTTP :: Site Management',
          'Topic :: Utilities',
          'Natural Language :: English',
      ],
      include_package_data=True,
      install_requires=[
          'python-wordpress-xmlrpc',
      ],
      long_description=open('README.rst').read(),
)
