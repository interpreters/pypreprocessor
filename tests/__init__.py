# -*- coding:utf-8 -*-
import sys
try:
    from setuptools import Command, setup
except ImportError:
    from distutils.core import Command, setup
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from tests import maintest
from tests import deprecationtest

class RunTests(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if(sys.stdout.encoding == 'utf-8'):
            print('╭─────────────────────────────────────╮')
            print('│                                     │')
            print('│              Test Start             │')
            print('│                                     │')
            print('╰─────────────────────────────────────╯')
        else:
            print('Test Start')
        import tests
        testSuite = unittest.TestSuite(tests.testsuite())
        runner = unittest.TextTestRunner(verbosity=2)
        results = runner.run(testSuite)
        sys.exit(0 if results.wasSuccessful() else 1)
        pass

def testsuite():
    suite = unittest.TestSuite()
    suite.addTests(maintest.testsuite())
    # suite.addTests(deprecationtest.testsuite())
    return suite