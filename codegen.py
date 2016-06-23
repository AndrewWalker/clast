import glud
from glud import *
from clastgen.utils import *
from clastgen.clangext import *
import ccsyspath
import collections
import os
import sys
import subprocess
import io


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
        self._meta[cursor.hash] = kwargs

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


def llvm_config(arg):
    llvm_home = os.environ['LLVM_HOME']
    llvm_config = os.path.join(llvm_home, 'bin', 'llvm-config')
    res = subprocess.check_output([llvm_config, arg]).split()
    if sys.version_info.major >= 3:
        return [p.decode('utf-8') for p in res]
    return res


def parse(src):
    syspath = ccsyspath.system_include_paths(os.path.join(os.environ['LLVM_HOME'], 'bin', 'clang++'))
    args = '-x c++ --std=c++11'.split()
    args += llvm_config('--cppflags')
    args += [ '-I' + inc for inc in syspath ]
    tu = glud.parse_string(src, name='input.cpp', args=args)
    return tu


def cxxRecordDeclEx(*args):
    return allOf(
                anyOf(
                    is_kind(CursorKind.STRUCT_DECL),
                    is_kind(CursorKind.CLASS_DECL)),
                *args)

def find_typedefs(tu, ctx):
    matcher = typedefDecl(
        hasName('string'), 
        hasAncestor(
            namespaceDecl(
                hasName('std'))))

    for n in walk(matcher, tu.cursor):
        ctx.add_typedef(n)

def find_classes(tu, ctx):
    matcher = cxxRecordDeclEx(
        isDefinition(),
        anyOf(
            hasTypename('llvm::StringRef'),
            hasTypename('clang::TypeSourceInfo'),
            hasTypename('clang::Type'),
            hasTypename('clang::QualType'),
            hasTypename('clang::Qualifiers'),
            hasTypename('clang::DeclContext'),
            hasTypename('clang::DeclarationName'),
            hasTypename('clang::DeclarationNameInfo'),
            hasTypename('clang::SourceLocation'),
            hasTypename('clang::SourceRange'),
            hasTypename('clang::SourceManager'),
            hasTypename('clang::ASTContext'),
            isSameOrDerivedFrom('clang::Decl'),
            isSameOrDerivedFrom('clang::Stmt')),
        unless(hasName('clang::FriendDecl')),
        unless(hasName('.*ObjC.*')),
        unless(hasName('.*OMP.*')))

    for n in walk(matcher, tu.cursor):
        ctx.add_class(n)


def find_methods(ctx):
    matcher = cxxMethodDecl(
        is_public,

        # don't bind static methods
        unless(hasStaticStorageDuration()),

        # foo* is ok, foo& is ok, foo*& is not
        unless(anyArgument(hasType(is_ref_to_ptr))),

        # foo* is ok, foo** is not
        unless(anyArgument(hasType(limit_indirections(1)))),
        unless(hasReturnType(limit_indirections(1))),
        unless(
            anyOf(
                hasName('Allocate'),
                hasName('.*begin'),
                hasName('begin.*'),
                hasName('.*end'),
                hasName('end.*'),
                hasName('operator.*')
            ))
        )
    for c in ctx.classes:
        for n in iter_child_nodes(matcher, c):
            ndecl = n.get_definition()
            if ndecl is None:
                print '// XXX', n.spelling
            elif ndecl != n:
                print '// YYY', n.spelling

            ctx.add_method(c, n)


def find_enums(ctx):
    res = {}
    for c, ms in ctx.methods.iteritems():
        for m in ms:
            for t in dependent_types(m):
                ut = underlying_type(t)
                decl = ut.get_declaration()
                if ut.kind == TypeKind.ENUM and decl is not None:
                    if not (is_protected(decl) or is_private(decl)):
                        res[decl.hash] = decl
    for decl in res.values():
        ctx.add_enum(decl)


def resolve_deleters(ctx):
    decl_subclass  = isSameOrDerivedFrom('clang::Decl')
    stmt_subclass  = isSameOrDerivedFrom('clang::Stmt')

    for c in ctx.classes:
        assert c is not None
        if decl_subclass(c):
            ctx.set_attr(c, deleter='decl_deleter<%s>::type' % c.type.spelling)
        if stmt_subclass(c):
            ctx.set_attr(c, deleter='stmt_deleter<%s>::type' % c.type.spelling)


def resolve_methods(ctx):
    for c in ctx.classes:
        for m in ctx.class_methods(c):
            if not is_resolved_method(m, ctx.classes + ctx.enums + ctx.typedefs):
                ctx.set_attr(m, is_disabled=True)    
            else:
                ctx.set_attr(m, is_disabled=False)
            if any(a.spelling == '' for a in m.get_arguments()):
                ctx.set_attr(m, mode='short')


def resolve_disabled_classes(ctx):
    exclusions = set([
        'llvm::StringRef'
    ])
    for c in ctx.classes:
        if c.type.spelling in exclusions:
            ctx.set_attr(c, is_disabled=True)    
        else:
            ctx.set_attr(c, is_disabled=False)


def render_type(t):
    tcan = t.get_canonical()
    kinds = [
        TypeKind.UNEXPOSED,
        TypeKind.TYPEDEF,
        TypeKind.LVALUEREFERENCE
    ]
    if t == tcan:
        return t.spelling
    else:
        return render_type(tcan)

def render_method(m, ctx):
    d = dict(
        mode            = 'long',
        parent          = m.semantic_parent.type.spelling,
        name            = m.spelling,
        typename        = m.type.spelling,
        signature       = method_signature(m),
        result_type     = render_type(m.result_type),
        arg_names       = [ n.spelling for n in m.get_arguments() ],
        arg_types       = [ render_type(n.type) for n in m.get_arguments() ],
        arg_kinds       = [ n.type.kind for n in m.get_arguments() ],
        is_virtual      = m.is_virtual_method(),
        is_pure_virtual = m.is_pure_virtual_method(),
        const           = 'const' if m.is_const_method() else '',
        is_overridden   = len(list(get_overridden_cursors(m))) > 0,
        is_overload     = is_overload(m),
        is_disabled     = False,
    )
    d.update(ctx.get_attr(m))
    return d

def render_enum(c, ctx):
    anon = 'anonymous enum at' in c.type.spelling
    parent = None
    if c.semantic_parent.kind == CursorKind.CLASS_DECL:
        parent = c.semantic_parent.type.spelling
    return dict(
        anon     = anon,
        name     = c.spelling,
        typename = c.type.spelling,
        parent   = parent,
        xitems   = [ n.spelling for n in c.get_children() ]
    )

def render_class(c, ctx):
    d = dict(
        name = c.spelling,
        typename = c.type.spelling,
        supers   = [],
        methods  = [ render_method(m, ctx) for m in ctx.class_methods(c) ],
        is_disabled = False,
    )
    d.update(ctx.get_attr(c))
    return d

def render_intermediate(ctx):
    d = dict(
        classes = [ render_class(c, ctx) for c in ctx.classes ],
        enums   = [ render_enum(c, ctx) for c in ctx.enums ],
    )
    return d


method_template = '''
        {%- if m.mode == 'short' %}
        {{ m|disabled }}.def("{{m.name}}", ({{ m.signature }})&{{ m.parent }}::{{ m.name }})
        {% else %}
        // {{ m.arg_types }}
        // {{ m.arg_kinds }}
        {{ m|disabled }}.def("{{ m.name }}", []({{ m.const }} {{ m.parent }}& self{{ m|argpack(call=False) }}) {{m|respack}} {
        {{ m|disabled }}   {{ m|retpack }}  self.{{m.name}}({{ m|argpack(call=True) }});
        {{ m|disabled }}})
        {% endif %}
'''

class_template = '''
    py::class_<{{cls.typename}}>(m, "{{cls.name}}")
    {% for m in cls.methods %}
        {% block context scoped %}
        {% include "method_template.j2" %}
        {% endblock context %}
    {% endfor %}
    ;

'''

enum_template = '''
    py::enum_<{{e.typename}}>({{ e|enum_parent }}, "{{e.typename|replace("::", "_")}}")
        {% for v in e.xitems %}
        .value("{{v}}", {{e.typename}}::{{v}})
        {% endfor %}
        .export_values();
    ;

'''

module_template = '''
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "internal.h"
{{ model.prelude }}


namespace py = pybind11;


void autogenerated_classes(pybind11::module& m)
{
    {% for cls in model.classes %}
    {% block c1 scoped %}
    {% if cls.is_disabled %}
    // Skipping generation of {{ cls.typename }}
    {% else %}
    {% include "class_template.j2" %}
    {% endif %}
    {% endblock c1 %}
    {% endfor %}

    {% for e in model.enums %}
    {% block c2 scoped %}
    {% include "enum_template.j2" %}
    {% endblock c2 %}
    {% endfor %}
}
'''

def enum_parent(e):
    if e['parent'] is not None:
        return 'py::base<%s>()' % e['typename']
    else:
        return 'm'

def argpack(method, call=True):
    if call:
        return ', '.join(n for n in method['arg_names'])
    else:
        return ' '.join(', %s %s' % (t, n) for t, n in zip(method['arg_types'], method['arg_names']))

def respack(method):
    if method['result_type'] == 'void':
        return ''
    else:
        return '-> %s' % method['result_type']

def retpack(method):
    if method['result_type'] == 'void':
        return ''
    else:
        return 'return' 

def disabled(o):
    return '//' if o['is_disabled'] else ''

def render_result(**kwargs):
    import jinja2
    from jinja2 import Environment, StrictUndefined
    templates = {
        'module.j2'          : module_template,
        'method_template.j2' : method_template,
        'class_template.j2'  : class_template,
        'enum_template.j2'   : enum_template,
    }
    loader = jinja2.DictLoader(templates)
    env = Environment(trim_blocks = True, lstrip_blocks = True,
                      undefined = StrictUndefined, 
                      loader=loader)
    env.filters['argpack'] = argpack
    env.filters['respack'] = respack
    env.filters['retpack'] = retpack
    env.filters['disabled'] = disabled
    env.filters['enum_parent'] = enum_parent
    return env.get_template('module.j2').render(model = kwargs)


def build_context(c_src):
    tu = parse(c_src)
    ctx = Context()
    find_typedefs(tu, ctx)
    find_classes(tu, ctx)
    find_methods(ctx)
    find_enums(ctx)
    resolve_deleters(ctx)
    resolve_methods(ctx)
    resolve_disabled_classes(ctx)
    return ctx

c_src = '''
#include <clang/AST/AST.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
'''

if __name__ == "__main__":

    ctx = build_context(c_src)
    print render_result(prelude=c_src, **render_intermediate(ctx)) 

