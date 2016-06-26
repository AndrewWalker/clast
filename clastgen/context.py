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
    def enums(self):
        return list(self._enums)

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


