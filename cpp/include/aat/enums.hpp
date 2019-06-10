#pragma once

#include <iostream>
#include <unordered_map>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include "common.h"

namespace py = pybind11;
PYBIND11_MAKE_OPAQUE(std::vector<std::string>);

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

    static const std::vector<std::string> TickType_names = {
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

    static std::unordered_map<std::string, TickType> _TickType_mapping = {
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

    ENUM_TO_STRING(TickType)
    ENUM_FROM_STRING(TickType)

    enum class ExchangeType {
        NONE = 0,
        SYNTHETIC = 1,
        COINBASE = 2,
        GEMINI = 3,
        KRAKEN = 4,
        POLONIEX = 5
    };

    static const std::vector<std::string> ExchangeType_names = {
        "NONE",
        "SYNTHETIC",
        "COINBASE",
        "GEMINI",
        "KRAKEN",
        "POLONIEX"
    };

    static std::unordered_map<std::string, ExchangeType> _ExchangeType_mapping = {
        {"NONE", ExchangeType::NONE},
        {"SYNTHETIC", ExchangeType::SYNTHETIC},
        {"COINBASE", ExchangeType::COINBASE},
        {"GEMINI", ExchangeType::GEMINI},
        {"KRAKEN", ExchangeType::KRAKEN},
        {"POLONIEX", ExchangeType::POLONIEX},
    };


    ENUM_TO_STRING(ExchangeType)
    ENUM_FROM_STRING(ExchangeType)

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

    py::bind_vector<std::vector<std::string>>(m, "StringVec");
    m.attr("TickTypes") = TickType_names;

    m.def("TickType_to_string", &TickType_to_string, "TickType enum to string");
    m.def("TickType_from_string", &TickType_from_string, "string to TickType enum");

    py::enum_<ExchangeType>(m, "ExchangeType", py::arithmetic())
        .value("NONE", ExchangeType::NONE)
        .value("SYNTHETIC", ExchangeType::SYNTHETIC)
        .value("COINBASE", ExchangeType::COINBASE)
        .value("GEMINI", ExchangeType::GEMINI)
        .value("KRAKEN", ExchangeType::KRAKEN)
        .value("POLONIEX", ExchangeType::POLONIEX);

    m.attr("ExchangeTypes") = ExchangeType_names;
    m.def("ExchangeType_to_string", &ExchangeType_to_string, "ExchangeType enum to string");
    m.def("ExchangeType_from_string", &ExchangeType_from_string, "string to ExchangeType enum");

}
