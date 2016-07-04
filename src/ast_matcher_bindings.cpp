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
                throw std::runtime_error("bad key");
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

    py::class_<clam::BoundNodes>(m, "BoundNodes")
    ;

    py::class_<clami::DynTypedMatcher>(m, "DynTypedMatcher")
        .def("getSupportedKind", &clami::DynTypedMatcher::getSupportedKind)
        .def("tryBind", [](const clami::DynTypedMatcher& self, const std::string& name) {
            return self.tryBind(name).getValue();
        });
    ;
}

