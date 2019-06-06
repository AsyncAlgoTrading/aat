#pragma once
#include <iostream>
#include <pybind11/pybind11.h>

namespace py = pybind11;

void say_hello(const char* name);

PYBIND11_MODULE(binding, m)
{
    m.doc() = "C++ bindings";
    m.def("say_hello", &say_hello, "A test function");
}
