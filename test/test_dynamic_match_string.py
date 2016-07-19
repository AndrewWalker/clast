from clast import *
import unittest

class DynamicMatcherTest(unittest.TestCase):
    """These are really smoke tests to make sure documenting expectations
    """

    def test_successful_parse(self):
        parseMatcherExpression('cxxRecordDecl()')

    def test_garbage_input(self):
        with self.assertRaises(RuntimeError):
            parseMatcherExpression('cxxRecordDecl')

    def test_failed_parse(self):
        with self.assertRaises(RuntimeError):
            parseMatcherExpression('cxxRecordDecl')

    def test_type_mismatch(self):
        with self.assertRaises(RuntimeError):
            parseMatcherExpression('callExpr(varDecl())')


if __name__ == '__main__':
    unittest.main()
