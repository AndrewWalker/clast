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


    def test_el2(self):

        class ForLoopHandler(MatchCallback):
            def __init__(self):
                # TODO : add rewriter argument
                super(ForLoopHandler, self).__init__()

            def run(self, result):
                incVar = result.GetNode('forLoop').get(VarDecl) 
                assert(incVar is not None)
                initStmt = incVar.getInit()
                condStmt = incVar.getCond()

        # https://github.com/eliben/llvm-clang-samples/blob/master/src_clang/matchers_rewriter.cpp
        s = '''forStmt(hasLoopInit(declStmt(hasSingleDecl(
                    varDecl(hasInitializer(integerLiteral()))
                        .bind("initVarName")))),
                hasIncrement(unaryOperator(
                    hasOperatorName("++"),
                    hasUnaryOperand(declRefExpr(to(
                        varDecl(hasType(isInteger())).bind("incVarName")))))),
                hasCondition(binaryOperator(
                    hasOperatorName("<"),
                    hasLHS(ignoringParenImpCasts(declRefExpr(to(
                        varDecl(hasType(isInteger())).bind("condVarName"))))),
                    hasRHS(expr(hasType(isInteger())))))).bind("forLoop")
        '''.replace('\n', '')

        m = parseMatcherExpression(s.replace('\n', ''))
        #m = parseMatcherExpression('forStmt(hasLoopInit(anything())).bind("forLoop")')
        callback = ForLoopHandler()
        finder = MatchFinder()
        finder.addDynamicMatcher(m, callback)
        matchString(code, finder, '-std=c++11', 'input.cpp')

    def test_el1(self):
        # http://eli.thegreenplace.net/2014/07/29/ast-matchers-and-clang-refactoring-tools
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

if __name__ == '__main__':
    unittest.main()
