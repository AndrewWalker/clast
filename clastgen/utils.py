from clang.cindex import *
from glud import *
from glud.predicates import *


def limit_indirections(n):
    def _limit_indirections(t):
        cnt = 0
        while t.kind == TypeKind.POINTER:
            t = t.get_pointee()
            cnt += 1
        return cnt > n
    return _limit_indirections


def is_ref_to_ptr(t):
    assert( type(t) == Type )
    return t.kind == TypeKind.LVALUEREFERENCE and t.get_pointee().kind == TypeKind.POINTER


def is_bool_ptr(c):
    """Test if a cursor refers to a boolean pointer
    """
    if not c.type.kind == TypeKind.POINTER:
        return False
    if not c.type.get_pointee().spelling == 'bool':
        return False
    return True


def is_anonymous_argument(c):
    """Test if one argument is anonymous (unnamed)

    In the declaration `void f(int x, int);` the second argument is unnamed
    """
    return c.spelling is None or c.spelling == ''


def has_any_anonymous_arguments(m):
    return any(is_anonymous_argument(a) for a in m.get_arguments())


def dependent_types(m):
    """Yield all of the types the method depends on
    """
    lst = [ m.result_type ]
    for arg in m.get_arguments():
        lst.append(arg.type)
    return lst


def method_signature(m):
    rt = m.result_type.spelling
    cls = m.semantic_parent.type.spelling
    args = ', '.join(a.type.spelling for a in m.get_arguments() )
    res = '%s (%s::*)(%s)' % (rt, cls, args)
    if m.is_const_method():
        return res + ' const'
    return res


def is_overload(c):
    it = iter_child_nodes(is_kind(CursorKind.CXX_METHOD), c.semantic_parent)
    names = [ m.spelling for m in it if m.spelling == c.spelling ]
    return len(names) > 1 


def fully_qualified(c):
    res = c.spelling
    c = c.semantic_parent
    while c.kind != CursorKind.TRANSLATION_UNIT:
        res = c.spelling + '::' + res
        c = c.semantic_parent
    return res


def underlying_type(t):
    """ Retrieve the simplest version of this type
    """
    if t.kind == TypeKind.POINTER:
        return underlying_type(t.get_pointee())
    elif t.kind == TypeKind.LVALUEREFERENCE:
        return underlying_type(t.get_pointee())
    elif t.kind == TypeKind.TYPEDEF:
        return underlying_type(t.get_canonical())
    if t.kind == TypeKind.UNEXPOSED:
        canonical = t.get_canonical()
        if canonical == t:
            return t
        else:
            return underlying_type(t.get_canonical())
    else:
        return t


def in_decl_set(decls, c):
    """ True if the cursor is in an sequence of cursor
    """
    for d in decls:
        if c == d:
            return True
    return False


def is_resolved_type(decls, t):
    """ True if a type exists in the context of a set of declarations
    """
    ut = underlying_type(t)
    if is_builtin(ut):
        return True
    elif in_decl_set(decls, ut.get_declaration()):
        return True
    return False


def is_resolved_method(m, decls):
    """ True if all a methods dependent types exist in a set of declarations
    """
    if not is_resolved_type(decls, m.result_type):
        return False
    for a in m.get_arguments():
        if not is_resolved_type(decls, a.type):
            return False
    return True
