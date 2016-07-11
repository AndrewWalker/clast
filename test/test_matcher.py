from clast import *

def test_simple_example():
    class MyMatchCallback(MatchCallback):
        def __init__(self, *args, **kwargs):
            super(MyMatchCallback, self).__init__()
    
        def run(self, result):
            cls = result.GetNode('cls').get(CXXRecordDecl)
            cls.dump()

    callback = MyMatchCallback()
    m = parseMatcherExpression('cxxRecordDecl().bind("cls")')
    finder = MatchFinder()
    finder.addDynamicMatcher(m, callback)
    matchString('class X;', finder, '-std=c++11', 'input.cpp')
