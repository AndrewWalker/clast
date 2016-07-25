//////////////////////////////////////////////////////////////////////////////
// Bindings for the clang::ast_matchers::dynamic namespace
//////////////////////////////////////////////////////////////////////////////
#include "pyclast.h"
#include "match_string.h"
#include <clang/AST/AST.h>
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/ASTMatchers/Dynamic/Parser.h>

namespace py = pybind11;
using namespace clang::ast_matchers;
using namespace clang::ast_matchers::internal;
using namespace clang::ast_matchers::dynamic;
using namespace clang::ast_type_traits;
//using namespace clang::tooling;


DynTypedMatcher parseMatcherExpression(const std::string& code)
{
  Diagnostics diagnostics;
  auto val = Parser::parseMatcherExpression(code, &diagnostics);
  if(false == val.hasValue()) {
    throw std::logic_error(diagnostics.toStringFull());
  }
  return val.getValue();
}



void install_wrappers(pybind11::module& m)
{
    py::class_<ASTNodeKind>(m, "ASTNodeKind")
        .def(py::init<>())
        .def("isSame", &ASTNodeKind::isSame)
        .def("isNone", &ASTNodeKind::isNone)
        .def("asStringRef", [](const ASTNodeKind& self){
            return std::string(self.asStringRef());
        })
        .def("__repr__", [](const ASTNodeKind& self){
            return std::string(self.asStringRef());
        })
        .def("hasPointerIdentity", &ASTNodeKind::hasPointerIdentity)
    ;

    py::class_<DynTypedMatcher>(m, "DynTypedMatcher")
        // returns an ASTNodeKind
        .def("getSupportedKind", &DynTypedMatcher::getSupportedKind)
        .def("tryBind", [](const DynTypedMatcher& self, const std::string& name) {
            return self.tryBind(name).getValue();
        });
    ;

    m.def("parseMatcherExpression", parseMatcherExpression);
    m.def("matchString", matchString);
}

