#include "pyclast.h"
#include <pybind11/stl.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchersInternal.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>
#include <cassert>

namespace py = pybind11;
namespace clam = clang::ast_matchers;
namespace clami = clang::ast_matchers::internal;
namespace clatt = clang::ast_type_traits;


namespace py = pybind11;

template<typename T>
clami::Matcher<T> try_convert(clami::DynTypedMatcher& arg)
{
    if(false == arg.canConvertTo<T>()) {
        throw std::runtime_error("invalid type");
    }
    return arg.convertTo<T>();
}


template<typename T>
llvm::ArrayRef<clami::Matcher<T>> convert(std::vector<clami::DynTypedMatcher>& args)
{
    std::vector<clami::Matcher<T>> v;
    for(size_t i = 0; i < args.size(); i++) {
        v.push_back(try_convert<T>(args.at(i)));
    }
    llvm::ArrayRef<clami::Matcher<T>> tmp(v);
    return tmp;
}

clami::DynTypedMatcher _cxxRecordDecl(std::vector<clami::DynTypedMatcher>& args) {
    return clam::cxxRecordDecl(convert<clang::CXXRecordDecl>(args));
}

clami::DynTypedMatcher _forStmt(std::vector<clami::DynTypedMatcher>& args) {
    return clam::forStmt(convert<clang::ForStmt>(args));
}

clami::DynTypedMatcher _hasLoopInit(clami::DynTypedMatcher& args) {
    return clam::hasLoopInit(try_convert<clang::Stmt>(args));
}

clami::DynTypedMatcher _decl(std::vector<clami::DynTypedMatcher>& args) {
    return clam::decl(convert<clang::Decl>(args));
}

clami::DynTypedMatcher _stmt(std::vector<clami::DynTypedMatcher>& args) {
    return clam::stmt(convert<clang::Stmt>(args));
}


//clami::DynTypedMatcher _binaryOperator(

void install_wrappers(pybind11::module& m)
{
    m.def("_decl", _decl);
    m.def("_stmt", _stmt);
    m.def("_forStmt", _forStmt);
    m.def("_hasLoopInit", _hasLoopInit);
    m.def("_cxxRecordDecl", _cxxRecordDecl);
}

