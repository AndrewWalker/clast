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

template<typename T, typename U>
clami::DynTypedMatcher execute(T& t, llvm::ArrayRef<clami::Matcher<U>>& args) {
    size_t len = args.size();
    if(len == 0) {
        return t();
    }
    else if(len == 1) {
        return t(args[0]);
    }
    else if(len == 2) {
        return t(args[0], args[1]);
    }
    else if(len == 3) {
        return t(args[0], args[1], args[2]);
    }
    else if(len == 4) {
        return t(args[0], args[1], args[2], args[3]);
    }
    throw std::logic_error("execute");
}


clami::DynTypedMatcher _cxxRecordDecl(std::vector<clami::DynTypedMatcher>& args) {
    auto val = convert<clang::CXXRecordDecl>(args);
    return execute(clam::cxxRecordDecl, val);
}

clami::DynTypedMatcher _forStmt(std::vector<clami::DynTypedMatcher>& args) {
    auto val = convert<clang::ForStmt>(args);
    return execute(clam::forStmt, val);
}

clami::DynTypedMatcher _hasLoopInit(clami::DynTypedMatcher& args) {
    return clam::hasLoopInit(try_convert<clang::Stmt>(args));
}

clami::DynTypedMatcher _decl(std::vector<clami::DynTypedMatcher>& args) {
    auto val = convert<clang::Decl>(args);
    return execute(clam::decl, val);
}

clami::DynTypedMatcher _stmt(std::vector<clami::DynTypedMatcher>& args) {
    auto val = convert<clang::Stmt>(args);
    return execute(clam::stmt, val);
}

clami::DynTypedMatcher _ifStmt(std::vector<clami::DynTypedMatcher>& args) {
    auto val =  convert<clang::Stmt>(args);
    return execute(clam::ifStmt, val);
}

clami::DynTypedMatcher _hasCondition(clami::DynTypedMatcher& arg) {
    auto tmp = clam::hasCondition(try_convert<clang::Expr>(arg));
    clami::Matcher<clang::AbstractConditionalOperator> m(tmp);
    return clami::DynTypedMatcher(m);
}


void install_wrappers(pybind11::module& m)
{
    m.def("_decl", _decl);
    m.def("_stmt", _stmt);
    m.def("_ifStmt", _stmt);
    m.def("_hasCondition", _hasCondition);
    m.def("_forStmt", _forStmt);
    m.def("_hasLoopInit", _hasLoopInit);
    m.def("_cxxRecordDecl", _cxxRecordDecl);
}

