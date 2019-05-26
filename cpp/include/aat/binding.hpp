#include <iostream>
#include <pybind11/pybind11.h>
namespace py = pybind11;

#ifndef __AAT_BINDING_HPP__
#define __AAT_BINDING_HPP__
void say_hello(const char* name);


PYBIND11_MODULE(test, m)
{
    m.doc() = "A Test";
    m.def("say_hello", &say_hello, "A test function");
}
#endif