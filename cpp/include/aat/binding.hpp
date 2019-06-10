#pragma once
#include <iostream>
#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(binding, m)
{
    m.doc() = "C++ bindings";
}
