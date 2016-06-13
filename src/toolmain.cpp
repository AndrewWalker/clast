#include "pyclast.h"
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <iostream>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Refactoring.h>
#include <clang/Tooling/Tooling.h>


namespace py = pybind11;
namespace clt = clang::tooling;

static llvm::cl::OptionCategory ClastCategory("Clast");


int toolmain(const std::vector<std::string>& args, clang::ast_matchers::MatchFinder& finder)
{
    int argc = static_cast<int>(args.size());
    const char** argv = new char const *[argc];
    for(int i = 0; i < argc; i++) 
    {
        argv[i] = args[i].c_str();
    }
    clang::tooling::CommonOptionsParser op(argc, argv, ClastCategory);
    for(auto v : op.getSourcePathList()) {
        std::cout << "source path " << v << std::endl;
    }
    clang::tooling::RefactoringTool tool(op.getCompilations(), op.getSourcePathList());
    return tool.run(clt::newFrontendActionFactory(&finder).get());
}

void install_toolmain(pybind11::module& m)
{
    m.def("toolmain", &toolmain);
}

