# -*- coding:utf-8 -*-
#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import unittest
from pypreprocessor import pypreprocessor
pypreprocessor.readEncoding = 'utf-8'
pypreprocessor.writeEncoding = 'utf-8'

from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    import io
    from io import StringIO

def testsuite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(FileParseTest))
    suite.addTests(unittest.makeSuite(CapturePrintTest))
    return suite

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
#exclude

# Template for other tests
class TestTemplate(object):
    def test_run_resume_save(self):
        pypreprocessor.run = True
        pypreprocessor.resume = True
        pypreprocessor.save = True
        pypreprocessor.parse()
        self.assertTrue(os.path.exists(pypreprocessor.output))
        pass

    def test_run_resume_nosave(self):
        pypreprocessor.run = True
        pypreprocessor.resume = True
        pypreprocessor.save = False
        pypreprocessor.parse()
        self.assertFalse(os.path.exists(pypreprocessor.output))
        pass

    def test_run_noresume_save(self):
        pypreprocessor.run = True
        pypreprocessor.resume = False
        pypreprocessor.save = True
        with self.assertRaises(SystemExit) as e:
            pypreprocessor.parse()
        self.assertEqual(e.exception.code, 0)
        self.assertTrue(os.path.exists(pypreprocessor.output))
        pass

    def test_run_noresume_nosave(self):
        pypreprocessor.run = True
        pypreprocessor.resume = False
        pypreprocessor.save = False
        with self.assertRaises(SystemExit) as e:
            pypreprocessor.parse()
        self.assertEqual(e.exception.code, 0)
        self.assertFalse(os.path.exists(pypreprocessor.output))
        pass
    
    def test_norun_resume_save(self):
        pypreprocessor.run = False
        pypreprocessor.resume = True
        pypreprocessor.save = True
        pypreprocessor.parse()
        self.assertTrue(os.path.exists(pypreprocessor.output))
        pass

    def test_norun_resume_nosave(self):
        pypreprocessor.run = False
        pypreprocessor.resume = True
        pypreprocessor.save = False
        pypreprocessor.parse()
        self.assertFalse(os.path.exists(pypreprocessor.output))
        pass

    def test_norun_noresume_save(self):
        pypreprocessor.run = False
        pypreprocessor.resume = False
        pypreprocessor.save = True
        with self.assertRaises(SystemExit) as e:
            pypreprocessor.parse()
        self.assertEqual(e.exception.code, 0)
        self.assertTrue(os.path.exists(pypreprocessor.output))
        pass

    def test_norun_noresume_nosave(self):
        pypreprocessor.run = False
        pypreprocessor.resume = False
        pypreprocessor.save = False
        with self.assertRaises(SystemExit) as e:
            pypreprocessor.parse()
        self.assertEqual(e.exception.code, 0)
        self.assertFalse(os.path.exists(pypreprocessor.output))
        pass

# Parses parsetarget.py
class FileParseTest(unittest.TestCase, TestTemplate):
    @classmethod
    def setUpClass(self):
        pypreprocessor.defines = []
        os.chdir('./tests')
        pass
    @classmethod
    def tearDownClass(self):
        os.chdir('./..')
        pass
    def setUp(self):
        super(FileParseTest, self).setUp()
        pypreprocessor.input = './parsetarget.py'
        pypreprocessor.output = self._testMethodName
        pass
    def tearDown(self):
        f = os.path.join(os.getcwd(), pypreprocessor.output)
        pypreprocessor.defines = []
        if(os.path.exists(f)):
            os.remove(f)
        super(FileParseTest, self).tearDown()
        pass
    pass

# Parses parsetarget.py with 'printTest' defined and captures print
class CapturePrintTest(unittest.TestCase, TestTemplate):
    @classmethod
    def setUpClass(self):
        os.chdir('./tests')
        pass

    @classmethod
    def tearDownClass(self):
        os.chdir('./..')
        pass

    def setUp(self):
        super(CapturePrintTest, self).setUp()
        pypreprocessor.defines = []
        pypreprocessor.defines.append('printTest')
        pypreprocessor.input = './parsetarget.py'
        pypreprocessor.output = self._testMethodName
        self.new_out, self.new_err = StringIO(), StringIO()
        self.old_out, self.old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self.new_out, self.new_err
        pass

    def tearDown(self):
        sys.stdout, sys.stderr = self.old_out, self.old_err
        if(pypreprocessor.run):
            lines = self.new_out.getvalue().strip().splitlines()
            self.assertIn('Hello, world!', lines)
            self.assertIn('가즈아ㅏㅏ', lines)
            self.assertIn('200', lines)
        else:
            self.assertEqual(self.new_out.getvalue().strip(), '')
        f = os.path.join(os.getcwd(), pypreprocessor.output)
        pypreprocessor.defines = []
        if(os.path.exists(f)):
            os.remove(f)
        super(CapturePrintTest, self).tearDown()
        pass
    pass
#endexclude

if(__name__ == 'main'):
    unittest.main()