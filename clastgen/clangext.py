import clang.cindex
import cymbal
import glud
from clang.cindex import *
from ctypes import *

clang_getOverriddenCursors = clang.cindex.conf.lib.clang_getOverriddenCursors
clang_getOverriddenCursors.restype = None
clang_getOverriddenCursors.argtypes = [Cursor, POINTER(POINTER(Cursor)), POINTER(c_uint)]

clang_disposeOverriddenCursors = clang.cindex.conf.lib.clang_disposeOverriddenCursors
clang_disposeOverriddenCursors.restype = None
clang_disposeOverriddenCursors.argtypes = [ POINTER(Cursor) ]

def get_overridden_cursors(self):
    cursors = POINTER(Cursor)()
    num = c_uint()
    clang_getOverriddenCursors(self, byref(cursors), byref(num))

    updcursors = []
    for i in range(int(num.value)):
        c = cursors[i]
        updcursor = Cursor.from_location(self._tu, c.location)
        updcursors.append( updcursor )

    clang_disposeOverriddenCursors(cursors)

    return updcursors

def patch_clang_commit_7cd277a1():
    tu = glud.parse_string('namespace N { class D {}; } N::D d;', args='-x c++ --std=c++11'.split())
    for c in tu.cursor.walk_preorder():
        try:
            # evaluating the property is sufficient
            c.type.kind
        except ValueError as ve:
            if c.type._kind_id == 119:
                TypeKind.ELABORATED = TypeKind(119)


def patch_clang_issue_28435():
    """Some (unstable) releases of the libclang bindings omit static_release
    """
    tu = glud.parse_string('int main() { static_assert(true, ""); return 0; }', args='-x c++ --std=c++11'.split())
    for c in tu.cursor.walk_preorder():
        try:
            # evaluating the property is sufficient
            c.kind
        except ValueError as ve:
            if c._kind_id == 602:
                CursorKind.STATIC_ASSERT = CursorKind(602)

cymbal.monkeypatch_type('get_template_argument_type',
                        'clang_Type_getTemplateArgumentAsType',
                        [Type, c_uint],
                        Type)

cymbal.monkeypatch_type('get_num_template_arguments',
                        'clang_Type_getNumTemplateArguments',
                        [Type],
                        c_int)

# fixed on master, but not in apt
patch_clang_commit_7cd277a1()

# bug reported, but not fixed 
patch_clang_issue_28435()
