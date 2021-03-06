//////////////////////////////////////////////////////////////////////////////
// top level composition of bindings
//////////////////////////////////////////////////////////////////////////////
#include "pyclast.h"

namespace py = pybind11;

PYBIND11_PLUGIN( _clast )
{
    py::module m("_clast");
    install_toolmain(m);
    install_wrappers(m);
    install_ast_matcher_bindings(m);
    autogenerated_classes(m);
    autogenerated_enums(m);
    install_dyntypednode(m);
    return m.ptr();
}
