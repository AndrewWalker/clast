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

void matchString(const std::string& code, MatchFinder& finder, 
                 const std::string& compileArgs = "-std=c++11", 
                 const std::string& filename = "input.cpp")
{
    const FileContentMappings &VirtualMappedFiles = FileContentMappings();
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
        VirtualMappedFiles);
}

void install_wrappers(pybind11::module& m)
{
    m.def("parseMatcherExpression", parseMatcherExpression);
    m.def("matchString", matchString);
}






