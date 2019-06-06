#pragma once

#include <iostream>
#include <unordered_map>
#include <pybind11/pybind11.h>
#include "common.h"

namespace py = pybind11;

enum class TickType {
    TRADE,
    OPEN,
    FILL,
    CANCEL,
    CHANGE,
    ERROR,
    ANALYZE,
    HALT,
    CONTINUE,
    EXIT,
    HEARTBEAT,
};

static const char *TickTypeNames[] = {
    "TRADE",
    "OPEN",
    "FILL",
    "CANCEL",
    "CHANGE",
    "ERROR",
    "ANALYZE",
    "HALT",
    "CONTINUE",
    "EXIT",
    "HEARTBEAT",
};

const char *to_string(TickType type)
{
  return TickTypeNames[static_cast<int>(type)];
}

static std::unordered_map<const char *, TickType> _mapping = {
        {(const char *)"TRADE", TickType::TRADE},
        {(const char *)"OPEN", TickType::OPEN},
        {(const char *)"FILL", TickType::FILL},
        {(const char *)"CANCEL", TickType::CANCEL},
        {(const char *)"CHANGE", TickType::CHANGE},
        {(const char *)"ERROR", TickType::ERROR},
        {(const char *)"ANALYZE", TickType::ANALYZE},
        {(const char *)"HALT", TickType::HALT},
        {(const char *)"CONTINUE", TickType::CONTINUE},
        {(const char *)"EXIT", TickType::EXIT},
        {(const char *)"HEARTBEAT", TickType::HEARTBEAT},
};

TickType from_string(char *s){ return _mapping[s]; }

PYBIND11_MODULE(_cpp_helpers, m)
{
    m.doc() = "C++ Helpers";
    py::enum_<TickType>(m, "TickType", py::arithmetic())
        .value("TRADE", TickType::TRADE)
        .value("OPEN", TickType::OPEN)
        .value("FILL", TickType::FILL)
        .value("CANCEL", TickType::CANCEL)
        .value("CHANGE", TickType::CHANGE)
        .value("ERROR", TickType::ERROR)
        .value("ANALYZE", TickType::ANALYZE)
        .value("HALT", TickType::HALT)
        .value("CONTINUE", TickType::CONTINUE)
        .value("EXIT", TickType::EXIT)
        .value("HEARTBEAT)", TickType::HEARTBEAT);

    m.def("to_string", &to_string, "TickType enum to string");
    m.def("from_string", &from_string, "string to TickType enum");

}
