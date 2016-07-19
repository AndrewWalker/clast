//////////////////////////////////////////////////////////////////////////////
// Bindings for the clang::MatchFinder and associated inner classes
//////////////////////////////////////////////////////////////////////////////
#include "pyclast.h"
#include <pybind11/stl.h>
#include <clang/AST/AST.h>
#include <clang/AST/ASTTypeTraits.h>
#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchersInternal.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

namespace py = pybind11;
namespace clam = clang::ast_matchers;
namespace clami = clang::ast_matchers::internal;
namespace clatt = clang::ast_type_traits;

class PyMatchCallback : public clam::MatchFinder::MatchCallback
{
public:
    using clam::MatchFinder::MatchCallback::MatchCallback;

    void run(const clam::MatchFinder::MatchResult& result) override
    {
        PYBIND11_OVERLOAD_PURE(
            void,
            clam::MatchFinder::MatchCallback,
            run,
            result
        );
    }

    void onStartOfTranslationUnit() override
    {
        PYBIND11_OVERLOAD(
            void,
            clam::MatchFinder::MatchCallback,
            onStartOfTranslationUnit,
        );
    }

    void onEndOfTranslationUnit() override
    {
        PYBIND11_OVERLOAD(
            void,
            clam::MatchFinder::MatchCallback,
            onEndOfTranslationUnit,
        );
    }
};



void install_ast_matcher_bindings(pybind11::module& m)
{
    py::class_<clam::MatchFinder::MatchResult>(m, "MatchResult")
        .def("SourceManager", [](const clam::MatchFinder::MatchResult& self) { 
            return self.SourceManager; 
        }, py::return_value_policy::reference)
        .def("GetNode", [](const clam::MatchFinder::MatchResult& self, const std::string& key) {
            auto it = self.Nodes.getMap().find(key);
            if(it == self.Nodes.getMap().end()){
                throw std::runtime_error("unknown node " + key);
            }
            clatt::DynTypedNode node = it->second;
            return node;
        })
        .def("Nodes", [](const clam::MatchFinder::MatchResult& self) { 
            return self.Nodes; 
        });

    py::class_<PyMatchCallback>(m, "MatchCallback")
        .alias<clam::MatchFinder::MatchCallback>()
        .def(py::init<>())
        .def("run", &PyMatchCallback::run)
        .def("onStartOfTranslationUnit", &PyMatchCallback::onStartOfTranslationUnit)
        .def("onEndOfTranslationUnit", &PyMatchCallback::onEndOfTranslationUnit)
        .def("getID", &PyMatchCallback::getID)
    ;

    py::class_<clam::MatchFinder>(m, "MatchFinder")
        .def(py::init<>())
        .def("addDynamicMatcher", &clam::MatchFinder::addDynamicMatcher)
        .def("matchAST",          &clam::MatchFinder::matchAST)
        .def("match", [](clam::MatchFinder& self, const clatt::DynTypedNode& node, clang::ASTContext& ctx){
            self.match(node, ctx);
        });
    ;

}

