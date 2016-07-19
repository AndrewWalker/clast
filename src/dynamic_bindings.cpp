//////////////////////////////////////////////////////////////////////////////
// Bindings for the clang::ast_matchers::dynamic namespace
//////////////////////////////////////////////////////////////////////////////
#include "pyclast.h"
#include <pybind11/stl.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchersInternal.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include "clang/ASTMatchers/Dynamic/Parser.h"
#include "clang/Frontend/ASTUnit.h"
#include "clang/Tooling/Tooling.h"

namespace py = pybind11;
using namespace clang::ast_matchers;
using namespace clang::ast_matchers::internal;
using namespace clang::ast_matchers::dynamic;
using namespace clang::tooling;


DynTypedMatcher parseMatcherExpression(const std::string& code)
{
  Diagnostics diagnostics;
  auto val = Parser::parseMatcherExpression(code, &diagnostics);
  if(false == val.hasValue()) {
    throw std::logic_error(diagnostics.toStringFull());
  }
  return val.getValue();
}

void matchString(const std::string& code, MatchFinder& finder, 
                 const std::string& compileArgs = "-std=c++11", 
                 const std::string& filename = "input.cpp")
{
    const FileContentMappings &virtualMappedFiles = FileContentMappings();
    std::unique_ptr<FrontendActionFactory> Factory(
        newFrontendActionFactory(&finder));
    std::vector<std::string> args = {compileArgs, "-frtti", "-fexceptions",
                                     "-target", "i386-unknown-unknown"};
    runToolOnCodeWithArgs(
        Factory->create(), code, args, filename, 
#if __clang_minor__ > 8
	"clang-tool",
#endif
    std::make_shared<clang::PCHContainerOperations>(), 
        virtualMappedFiles);
}

void install_wrappers(pybind11::module& m)
{
    py::class_<clatt::ASTNodeKind>(m, "ASTNodeKind")
        .def(py::init<>())
        .def("isSame", &clang::ast_type_traits::ASTNodeKind::isSame)
        .def("isNone", &clang::ast_type_traits::ASTNodeKind::isNone)
        .def("asStringRef", [](const clatt::ASTNodeKind& self){
            return std::string(self.asStringRef());
        })
        .def("__repr__", [](const clatt::ASTNodeKind& self){
            return std::string(self.asStringRef());
        })
        .def("hasPointerIdentity", &clang::ast_type_traits::ASTNodeKind::hasPointerIdentity)
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

