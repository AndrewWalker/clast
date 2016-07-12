import collections
from .utils import *

__all__ = ['Context']


class Context(object):
    def __init__(self):
        self._enums = []
        self._classes = []
        self._typedefs = []
        self._methods = collections.defaultdict(list)
        self._meta = {}
        self._prelude = ''
        self._clang_version = ''

    def set_clang_version(self, version):
        self._clang_version = version

    def set_prelude(self, src):
        self._prelude = src

    def add_typedef(self, cursor):
        decl = underlying_type(cursor.get_definition().type).get_declaration()
        self._typedefs.append(decl)

    def add_class(self, cursor):
        self._classes.append(cursor)

    def add_method(self, cls, method):
        self._methods[cls.hash].append(method)

    def add_enum(self, enum):
        self._enums.append(enum)

    def get_attr(self, cursor):
        return self._meta.get(cursor.hash, {})

    def set_attr(self, cursor, **kwargs):
        if cursor.hash not in self._meta:
            self._meta[cursor.hash] = {}
        self._meta[cursor.hash].update(kwargs)

    @property
    def clang_version(self):
        return self._clang_version

    @property
    def prelude(self):
        return self._prelude

    @property
    def enums(self):
        # guarantee a stable sort order
        lst = list(self._enums)
        lst.sort(key = lambda e : e.type.spelling)
        return lst

    @property
    def classes(self):
        return list(self._classes)

    @property
    def typedefs(self):
        return list(self._typedefs)

    @property
    def methods(self):
        return self._methods

    def class_methods(self, cursor):
        return self._methods[cursor.hash]

    def enabled_methods(self):
        for c in self.classes:
            for m in self.class_methods(c):
                attrs = self.get_attr(m)
                if not attrs['is_disabled']:
                    yield c, m


