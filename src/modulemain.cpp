#include "pyclast.h"

namespace py = pybind11;

PYBIND11_PLUGIN( pyclast )
{
    py::module m("pyclast");
    install_toolmain(m);
    return m.ptr();
}
