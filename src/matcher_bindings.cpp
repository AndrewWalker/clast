#include "pyclast.h"
#include <pybind11/stl.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchersInternal.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include "clang/ASTMatchers/Dynamic/Parser.h"
#include <cassert>

namespace py = pybind11;
using namespace clang::ast_matchers;
using namespace clang::ast_matchers::internal;
using namespace clang::ast_matchers::dynamic;


// FIXME: This is a temporary placeholder until a better solution can be found
DynTypedMatcher parseMatcherExpression(const std::string& code)
{
  Diagnostics Err;
  auto val = Parser::parseMatcherExpression(code, &Err);
  if(false == val.hasValue()) {
    throw std::logic_error("parse failed");
  }
  return val.getValue();
}

void install_wrappers(pybind11::module& m)
{
    m.def("parseMatcherExpression", parseMatcherExpression);
}

