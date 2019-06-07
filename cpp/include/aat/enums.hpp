#pragma once

#include <iostream>
#include <unordered_map>
#include <pybind11/pybind11.h>
#include "common.h"

namespace py = pybind11;

namespace aat {
namespace enums {

    enum class TickType {
        TRADE = 0,
        OPEN = 1,
        FILL = 2,
        CANCEL = 3,
        CHANGE = 4,
        ERROR = 5,
        ANALYZE = 6,
        HALT = 7,
        CONTINUE = 8,
        EXIT = 9,
        HEARTBEAT = 10
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

    static std::unordered_map<std::string, TickType> _mapping = {
            {"TRADE", TickType::TRADE},
            {"OPEN", TickType::OPEN},
            {"FILL", TickType::FILL},
            {"CANCEL", TickType::CANCEL},
            {"CHANGE", TickType::CHANGE},
            {"ERROR", TickType::ERROR},
            {"ANALYZE", TickType::ANALYZE},
            {"HALT", TickType::HALT},
            {"CONTINUE", TickType::CONTINUE},
            {"EXIT", TickType::EXIT},
            {"HEARTBEAT", TickType::HEARTBEAT},
    };

    TickType from_string(char *s)
    { 
        return _mapping[s];
    }
}
}


PYBIND11_MODULE(_enums, m)
{
    m.doc() = "C++ enums";
    using namespace aat::enums;
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
        .value("HEARTBEAT", TickType::HEARTBEAT);

    m.def("to_string", &to_string, "TickType enum to string");
    m.def("from_string", &from_string, "string to TickType enum");

}
