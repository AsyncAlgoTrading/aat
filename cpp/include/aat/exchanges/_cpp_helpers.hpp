#include <iostream>
#include <pybind11/pybind11.h>
namespace py = pybind11;

#ifndef __AAT_CPP_HELPERS_HPP__
#define __AAT_CPP_HELPERS_HPP__
void test();

PYBIND11_MODULE(_cpp_helpers, m)
{
    m.doc() = "A Test";
    m.def("test", &test, "A test function");
}
#endif