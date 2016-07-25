//////////////////////////////////////////////////////////////////////////////
// Bindings for the clang::ast_matchers::dynamic namespace
//////////////////////////////////////////////////////////////////////////////
#ifndef CLAST_MATCH_STRING_H
#define CLAST_MATCH_STRING_H

#include <string>
#include <vector>
#include <clang/ASTMatchers/ASTMatchFinder.h>

void matchString(const std::string& code, 
                 clang::ast_matchers::MatchFinder& finder, 
                 const std::vector<std::string>& args, 
                 const std::string& filename);

#endif
