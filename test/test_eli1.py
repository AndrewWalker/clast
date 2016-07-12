from clast import *

code = '''int foo(int* p, int v) {
  if (p == 0) {
    return v + 1;
  } else {
    return v - 1;
  }
}  
'''

def test_eli1():
    """Smoke test for AST matching
    """

    # http://eli.thegreenplace.net/2014/07/29/ast-matchers-and-clang-refactoring-tools
    class MyMatchCallback(MatchCallback):
        def __init__(self, *args, **kwargs):
            super(MyMatchCallback, self).__init__()
    
        def run(self, result):
            s = result.GetNode('op').get(Stmt)
            sm = result.SourceManager()
            loc = s.getLocStart()

            # TODO - Incomplete, col and line should be tuples
            res = False
            col = sm.getSpellingColumnNumber(loc, res)
            line= sm.getSpellingLineNumber(loc, res)

    callback = MyMatchCallback()
    m = parseMatcherExpression('ifStmt(hasCondition(binaryOperator(hasOperatorName("==")))).bind("op")')
    finder = MatchFinder()
    finder.addDynamicMatcher(m, callback)
    matchString(code, finder, '-std=c++11', 'input.cpp')
    

test_eli1()
