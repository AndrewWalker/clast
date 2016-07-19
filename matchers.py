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
import os
import sys
import subprocess
import io
import json


def clang_version():
    llvm_home = os.environ['LLVM_HOME']
    binary = os.path.join(llvm_home, 'bin', 'clang')
    res = subprocess.check_output([binary, '--version']).splitlines()[0]
    if sys.version_info.major >= 3:
        return res.decode('utf-8')
    return res


def llvm_config(arg):
    llvm_home = os.environ['LLVM_HOME']
    llvm_config = os.path.join(llvm_home, 'bin', 'llvm-config')
    res = subprocess.check_output([llvm_config, arg]).split()
    if sys.version_info.major >= 3:
        return [p.decode('utf-8') for p in res]
    return res


def parse(src):
    syspath = ccsyspath.system_include_paths(os.path.join(os.environ['LLVM_HOME'], 'bin', 'clang++'))
    syspath = [ p.decode('utf-8') for p in syspath ]
    args = '-x c++ --std=c++11'.split()
    args += llvm_config('--cppflags')
    args += [ '-I' + inc for inc in syspath ]
    tu = glud.parse_string(src, name='input.cpp', args=args)
    return tu


c_src = '''
#include <clang/AST/AST.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
'''

from asciitree import draw_tree


def dump(cursor):
    def node_children(node):
        if node.kind == CursorKind.COMPOUND_STMT:
            return []
        return list(node.get_children())

    def print_node(node):
        text = node.spelling or node.displayname
        kind = str(node.kind).split('.')[1]
        return '{} {}'.format(kind, text)

    return draw_tree(cursor, node_children, print_node)


def is_clami_matcher(t):
    if t.startswith('clang::ast_matchers::internal::Matcher'):
        return True
    if t.startswith('const clang::ast_matchers::internal::Matcher'):
        return True
    return False
            

def render_result(templates, template, **kwargs):
    import jinja2
    from jinja2 import environment, strictundefined
    
    loader = jinja2.dictloader(templates)
    env = environment(trim_blocks = true, lstrip_blocks = true,
                      undefined = strictundefined, 
                      loader=loader)
    env.filters.update()
    return env.get_template(template).render(**kwargs)


matcher_0 = '''
clami::DynTypedMatcher _{{ f.name }}()
{
    return {{ f.name }}();
}
'''

matcher_1 = '''
clami::DynTypedMatcher _{{ f.name }}(clami::DynTypedMatcher& m)
{
    return {{ f.name }}(try_convert<>);
}
'''


def matcher_0_pred(f):
    if not is_clami_matcher(f['result_type']):
        return False
    if len(f['args']) != 0:
        return False
    return True

def matcher_1_pred(f):
    if not is_clami_matcher(f['result_type']):
        return False
    if len(f['args']) != 1 or not is_clami_matcher(f['args'][0][0]):
        return False
    return True


def render_template_args(atype):
    if atype.kind == TypeKind.LVALUEREFERENCE:
        atype = atype.get_pointee()
    ttypes = []
    for i in range(atype.get_num_template_arguments()):
        ttypes.append( atype.get_template_argument_type(i).spelling )
    return ttypes


def render_type(a):
    atype = a.get_canonical()
    d = dict(
        typename = atype.spelling,
        template_args = render_template_args(atype),
    )
    return d


def render_arg(a):
    d = render_type(a.type)
    d['name'] = a.spelling
    return d


if __name__ == "__main__":
    if 'LLVM_HOME' not in os.environ:
        print('LLVM_HOME is undefined, giving up on code generation')
        sys.exit(1)

    tu = parse(c_src)
    m = allOf(
            isExpansionInFileMatching('.*ASTMatchers.h'),
            anyOf(
                functionDecl(),
                varDecl()),
            hasParent(namespaceDecl(hasName('ast_matchers'))))
    intermediate = []
    for c in tu.cursor.walk_preorder():
        if m(c):
            if c.kind == CursorKind.FUNCTION_DECL:
                #print(c.kind, c.spelling)
                #print([ a.type.spelling for a in c.get_arguments() ]), '->', c.result_type.spelling
                d = dict(
                    name = c.spelling,
                    result_type = render_type(c.result_type),
                    args = [ render_arg(a) for a in c.get_arguments() ]
                )
                intermediate.append(d)
            else:
                pass
    # templates = {
        # 'matcher_0' : matcher_0,
    # }
    # for f in intermediate:
        # if matcher_0_pred(f):
            # pass 
        # elif matcher_1_pred(f):
            # print f
        #else:
        #    print f

    print json.dumps(intermediate, indent=4)
    # for f in intermediate:
        # if f['result_type'].startswith('clang::ast_matchers::internal::Matcher'):
            # print '%s %s(clang::ast_matchers::internal DynTypedMatcher
