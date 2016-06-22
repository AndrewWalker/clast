import clang.cindex
import cymbal
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
    for i in xrange(int(num.value)):
        c = cursors[i]
        updcursor = Cursor.from_location(self._tu, c.location)
        updcursors.append( updcursor )

    clang_disposeOverriddenCursors(cursors)

    return updcursors

cymbal.monkeypatch_type('get_template_argument_type',
                        'clang_Type_getTemplateArgumentAsType',
                        [Type, c_uint],
                        Type)

cymbal.monkeypatch_type('get_num_template_arguments',
                        'clang_Type_getNumTemplateArguments',
                        [Type],
                        c_int)


