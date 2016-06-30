#ifndef PYCLAST_INTERNAL_H
#define PYCLAST_INTERNAL_H

#include <clang/AST/AST.h>

template<class T>
struct nopdeleter {
    void operator()(T* t) {
    }
};

template<class T>
struct stmt_deleter
{
    typedef std::unique_ptr<T, nopdeleter<clang::Stmt>> type;
};

template<class T>
struct decl_deleter
{
    typedef std::unique_ptr<T, nopdeleter<clang::Decl>> type;
};

#endif

