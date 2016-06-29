import _clast

## REPRESENTATIVE CLASSES ONLY

def cxxRecordDecl(*args):
    return pyclast._cxxRecordDecl(list(args))

def decl(*args):
    return pyclast._decl(list(args))

def stmt(*args):
    return pyclast._stmt(list(args))

def forStmt(*args):
    return pyclast._forStmt(list(args))

def hasLoopInit(arg):
    return pyclast._hasLoopInit(arg)


