import _clast
from _clast import *

## REPRESENTATIVE CLASSES ONLY

def cxxRecordDecl(*args):
    return _clast._cxxRecordDecl(list(args))

def decl(*args):
    return _clast._decl(list(args))

def stmt(*args):
    return _clast._stmt(list(args))

def forStmt(*args):
    return _clast._forStmt(list(args))

def hasLoopInit(arg):
    return _clast._hasLoopInit(arg)


