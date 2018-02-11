try:
    import unittest2 as unittest
except ImportError:
    import unittest
from tests import maintest
from tests import deprecationtest

def testsuite():
    suite = unittest.TestSuite()
    suite.addTests(maintest.testsuite())
    # suite.addTests(deprecationtest.testsuite())
    return suite