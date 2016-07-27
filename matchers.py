#!/usr/bin/env python
import glud
from glud import *
from clastgen.tools import *
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


def dump(cursor, pred=anything()):
    def node_children(node):
        return iter_node_children(pred, node)

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

    # The most simple form of matcher: 
    #  - Matcher<something> f()
    m0 = functionDecl(
            parameterCountIs(0),
            hasReturnType(
                hasCanonicalType(
                    anyOf(
                        hasName('clang::ast_matchers::internal::Matcher.*')))))

    # Special case of m0 where a proxy class needs to returned
    m0p = functionDecl(
            parameterCountIs(0),
            hasReturnType(
                hasCanonicalType(
                    hasName('clang::ast_matchers::internal::PolymorphicMatcherWithParam0.*'))))

    # The most common form of matcher: 
    #  - Matcher<something> f(matcher<something>)
    #  - BindableMatcher<something> g(matcher<something>)
    m1 = functionDecl(
            parameterCountIs(1),
            hasParameter(0, 
                hasType(
                    hasCanonicalType(
                        hasName('.*clang::ast_matchers::internal::Matcher.*')))),
            hasReturnType(
                hasCanonicalType(
                    anyOf(
                        hasName('clang::ast_matchers::internal::Matcher.*'),
                        hasName('clang::ast_matchers::internal::BindableMatcher.*')))))

    # Special case of m1 where a proxy class needs to be returned
    m1p = functionDecl(
            parameterCountIs(1),
            hasParameter(0, 
                hasType(
                    hasCanonicalType(
                        hasName('.*clang::ast_matchers::internal::Matcher.*')))),
            hasReturnType(
                hasCanonicalType(
                    hasName('clang::ast_matchers::internal::PolymorphicMatcherWithParam1.*'))))

    # Special case of m1 where there is only a data argument 
    m1a = functionDecl(
            parameterCountIs(1),
            hasParameter(0, 
                hasType(
                    hasCanonicalType(
                        anyOf(
                            hasName('.*std::string.*'),
                            hasName('.*unsigned int.*'))))),
            hasReturnType(
                hasCanonicalType(
                    hasName('clang::ast_matchers::internal::Matcher.*'))))

    # m2 = functionDecl(
            # parameterCountIs(0),
            # hasReturnType(
                # hasCanonicalType(
                    # hasName('clang::ast_matchers::internal::Matcher.*'))))


    ms = [
        NodeMatcher(m0, 'matcher_0'),
        NodeMatcher(m1, 'matcher_1'),
        NodeMatcher(functionDecl(), '???')
    ]

    mbase = allOf(
        isExpansionInFileMatching('.*ASTMatchers.h'),
        hasParent(namespaceDecl(hasName('ast_matchers'))))
    cursors = glud.walk(mbase, tu.cursor)
    mprime = functionDecl()
    import collections
    import pprint
    d = collections.defaultdict(list)
    for c in cursors:
        if mprime(c):
            args = list(c.get_arguments())
            if m0(c):
                print 'm0', c.spelling
            elif m0p(c):
                print 'pm0', c.spelling
            elif m1(c):
                print 'm1', c.spelling
            elif m1p(c):
                print 'pm1', c.spelling
            elif m1a(c):
                print 'm1a', c.spelling
            else:
                inter = {
                    'name' : c.spelling,
                    'result_type': c.result_type.get_canonical().spelling,
                    'args': [(a.type.spelling, a.spelling) for a in args],
                    'nargs' : len(args),
                }
                pprint.pprint(inter)
                #print c.spelling, c.result_type.get_canonical().spelling, 'xx')
        # for m in ms:
            # if m.match(c):
                # d[m._template].append(c)
                # # print m._template, c.spelling
                # break
    # pprint.pprint(dict(d))
    # for f in d['???']:
        # print f.result_type.get_canonical().spelling, len(list(f.get_arguments())), f.spelling
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
