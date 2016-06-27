from clang.cindex import *
from .utils import *
from .clangext import *

__all__ = ['render_intermediate']

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
        filename = c.location.file.name,
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


