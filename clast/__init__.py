import _clast
from _clast import *

def __get(self, kind):
    return getattr(self, '_get_' + kind.__name__)()

# Monkey patch an extra method on that we can't do in C++
_clast.DynTypedNode.get = __get
