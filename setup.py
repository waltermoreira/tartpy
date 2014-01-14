#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name='tartpy',
      version='0.1.0',
      description='Tiny Actor Run-Time in Python.',
      url='http://github.com/waltermoreira/tartpy',
      author='Walter Moreira',
      author_email='walter@waltermoreira.net',
      packages=find_packages(),
      license='GPLv3',
      long_description=open('README.rst').read(),
      install_requires=[
          "pytest >= 2.4",
      ]
)
