#include <iostream>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>

#ifndef __AAT_CPP_HELPERS_HPP__
#define __AAT_CPP_HELPERS_HPP__
void test();

BOOST_PYTHON_MODULE(_cpp_helpers)
{
    boost::python::def("test", test);
}
#endif