import unittest

# load testsuites from module.
from tests import sourceslist

def suite():
    suite = unittest.TestSuite()
    suite.addTest(sourceslist.suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
