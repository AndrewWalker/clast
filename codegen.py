#!/usr/bin/env python
import glud
from glud import *
from clastgen.utils import *
from clastgen.clangext import *
from clastgen.context import *
from clastgen.filters import *
from clastgen.intermediate import *
from clastgen.templates import *
from clastgen.pagination import *
import ccsyspath
import collections
import os
import sys
import subprocess
import io



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
        #print type(c), c.type.spelling, decl_subclass(c), stmt_subclass(c)
        assert c is not None
        assert type(c) == Cursor
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


def render_result(template, model, **kwargs):
    import jinja2
    from jinja2 import Environment, StrictUndefined
    
    loader = jinja2.DictLoader(clast_templates())
    env = Environment(trim_blocks = True, lstrip_blocks = True,
                      undefined = StrictUndefined, 
                      loader=loader)
    env.filters.update(clast_jinja_filters())
    return env.get_template(template).render(model = model, **kwargs)


def build_context(tu):
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
    import json
    import argparse

    parser = argparse.ArgumentParser('Generate clast code')
    parser.add_argument('-o', '--output',
                          help    = 'output directory');
    args = parser.parse_args(sys.argv[1:])

    tu = parse(c_src)
    ctx = build_context(tu)
    ctx.set_prelude(c_src)

    intermediate = render_intermediate(ctx)
    with open(os.path.join(args.output, 'intermediate.json'), 'w') as fh:
        fh.write(json.dumps(intermediate, indent=4))
    with open(os.path.join(args.output, '00_autogen_enums.cpp'), 'w') as fh:
        fh.write(render_result(template='enum_module.j2', model=intermediate)) 

    classargs = dict(
        template='class_module.j2', 
        model=intermediate)
    for pageno, pgstart, pgend in pagination(ctx.classes, 20):    
        fname = '%02d_autogen_classes.cpp' % (pageno+1)
        classargs['pageno']  = pageno
        classargs['pgstart'] = pgstart
        classargs['pgend']   = pgend
        with open(os.path.join(args.output, fname), 'w') as fh:
            fh.write(render_result(**classargs)) 

