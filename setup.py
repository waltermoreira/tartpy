#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--ignore', 'build']
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(name='tartpy',
      version='0.1.0',
      description='Tiny Actor Run-Time in Python.',
      url='http://github.com/waltermoreira/tartpy',
      author='Walter Moreira',
      author_email='walter@waltermoreira.net',
      packages=find_packages(),
      license='MIT',
      long_description=open('README.rst').read(),
      cmdclass = {'test': PyTest},
      install_requires=[
          "pytest >= 2.4",
          "Logbook",
      ],
      tests_require=['pytest']
)
