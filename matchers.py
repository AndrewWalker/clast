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
import jinja2
from jinja2 import Environment, StrictUndefined


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


def render_function(f):
    d = dict(
        name = f.spelling,
        result_type = render_type(f.result_type),
        args = [ render_arg(a) for a in f.get_arguments() ]
    )
    return d


class NodeMatcher(object):
    def __init__(self, m, template):
        self._m = m
        self._template = template

    def match(self, c):
        return self._m(c)

    def intermediate(self, c):
        return render_function(c)


# def render_all():
    # loader = jinja2.DictLoader(templates)
    # env = Environment(trim_blocks = true, lstrip_blocks = true,
                      # undefined = StrictUndefined, 
                      # loader=loader)
    # return env.get_template(template).render(**kwargs)



if __name__ == "__main__":
    if 'LLVM_HOME' not in os.environ:
        print('LLVM_HOME is undefined, giving up on code generation')
        sys.exit(1)

    tu = parse(c_src)

    m0 = functionDecl(
            argumentCountIs(0),
            hasReturnType(
                hasCanonicalType(
                    hasName('clang::ast_matchers::internal::Matcher.*'))))

    m1 = functionDecl(
            argumentCountIs(1),
            hasReturnType(
                hasCanonicalType(
                    hasName('clang::ast_matchers::internal::Matcher.*'))))

    ms = [
        NodeMatcher(m0, 'matcher_0'),
        NodeMatcher(m1, 'matcher_1'),
        NodeMatcher(functionDecl(), '???')
    ]

    mbase = allOf(
        isExpansionInFileMatching('.*ASTMatchers.h'),
        hasParent(namespaceDecl(hasName('ast_matchers'))))
    cursors = glud.walk(mbase, tu.cursor)

    import collections
    import pprint
    d = collections.defaultdict(list)
    for c in cursors:
        for m in ms:
            if m.match(c):
                d[m._template].append(c)
                # print m._template, c.spelling
                break
    pprint.pprint(dict(d))
    for f in d['???']:
        print f.result_type.get_canonical().spelling, len(list(f.get_arguments())), f.spelling
    # functions = []
    # for c in glud.walk(m, tu.cursor):
        # functions.append(render_function(c))



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

    # print json.dumps(intermediate, indent=4)
    # for f in intermediate:
        # if f['result_type'].startswith('clang::ast_matchers::internal::Matcher'):
            # print '%s %s(clang::ast_matchers::internal DynTypedMatcher
