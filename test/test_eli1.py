from clast import *
import unittest

code = '''int foo(int* p, int v) {
  if (p == 0) {
    return v + 1;
  } else {
    return v - 1;
  }
}  
'''

class EliTest(unittest.TestCase):
    # http://eli.thegreenplace.net/2014/07/29/ast-matchers-and-clang-refactoring-tools


    def test_el1(self):
        class MyMatchCallback(MatchCallback):
            def __init__(self, *args, **kwargs):
                super(MyMatchCallback, self).__init__()
                self.matches = []
        
            def run(self, result):
                s = result.GetNode('op').get(Stmt)
                loc = s.getLocStart()
                sm = result.SourceManager()
                col = sm.getSpellingColumnNumber(loc)
                line= sm.getSpellingLineNumber(loc)
                self.matches.append( (col, line) )    
 
        callback = MyMatchCallback()
        m = parseMatcherExpression('ifStmt(hasCondition(binaryOperator(hasOperatorName("==")).bind("op")))')
        finder = MatchFinder()
        finder.addDynamicMatcher(m, callback)
        matchString(code, finder, '-std=c++11', 'input.cpp')
        self.assertEquals((7,2), callback.matches[0])

