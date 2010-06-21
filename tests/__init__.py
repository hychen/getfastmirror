import unittest

# load testsuites from module.
from tests import sourceslist, console

def suite():
    suite = unittest.TestSuite()
    suite.addTest(sourceslist.suite())
    suite.addTest(console.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
