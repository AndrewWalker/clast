#include "match_string.h"
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/Dynamic/Parser.h>
#include <clang/Tooling/Tooling.h>

using namespace clang::ast_matchers;
using namespace clang::ast_matchers::internal;
using namespace clang::ast_matchers::dynamic;
using namespace clang::ast_type_traits;
using namespace clang::tooling;


void matchString(const std::string& code, MatchFinder& finder, 
                 const std::vector<std::string>& compileArgs, 
                 const std::string& filename)
{
    const FileContentMappings &virtualMappedFiles = FileContentMappings();
    std::unique_ptr<FrontendActionFactory> Factory(
        newFrontendActionFactory(&finder));
    std::vector<std::string> args = compileArgs;
    args.insert(args.end(), {"-frtti", "-fexceptions",
                                     "-target", "i386-unknown-unknown"});
    runToolOnCodeWithArgs(
        Factory->create(), 
        llvm::Twine(code), args, llvm::Twine(filename), 
        llvm::Twine("clang-tool"),
        std::make_shared<clang::PCHContainerOperations>(), 
        virtualMappedFiles);
}
