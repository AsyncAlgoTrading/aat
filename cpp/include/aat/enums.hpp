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

    enum class EventType {
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

    enum class DataType {
        ORDER = 0,
        TRADE = 1,
    };


    static const std::vector<std::string> EventType_names = {
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

    static const std::vector<std::string> DataType_names = {
        "ORDER",
        "TRADE",
    };

    static std::unordered_map<std::string, EventType> _EventType_mapping = {
            {"TRADE", EventType::TRADE},
            {"OPEN", EventType::OPEN},
            {"FILL", EventType::FILL},
            {"CANCEL", EventType::CANCEL},
            {"CHANGE", EventType::CHANGE},
            {"ERROR", EventType::ERROR},
            {"ANALYZE", EventType::ANALYZE},
            {"HALT", EventType::HALT},
            {"CONTINUE", EventType::CONTINUE},
            {"EXIT", EventType::EXIT},
            {"HEARTBEAT", EventType::HEARTBEAT},
    };

    static std::unordered_map<std::string, DataType> _DataType_mapping = {
            {"ORDER", DataType::ORDER},
            {"TRADE", DataType::TRADE},
    };

    ENUM_TO_STRING(EventType)
    ENUM_TO_STRING(DataType)
    ENUM_FROM_STRING(EventType)
    ENUM_FROM_STRING(DataType)

    enum class ExchangeType {
        NONE = 0,
        SYNTHETIC = 1,
    };

    static const std::vector<std::string> ExchangeType_names = {
        "NONE",
        "SYNTHETIC",
    };

    static std::unordered_map<std::string, ExchangeType> _ExchangeType_mapping = {
        {"NONE", ExchangeType::NONE},
        {"SYNTHETIC", ExchangeType::SYNTHETIC},
    };


    ENUM_TO_STRING(ExchangeType)
    ENUM_FROM_STRING(ExchangeType)

}
}



PYBIND11_MODULE(_enums, m)
{
    m.doc() = "C++ enums";
    using namespace aat::enums;
    py::enum_<EventType>(m, "EventType", py::arithmetic())
        .value("TRADE", EventType::TRADE)
        .value("OPEN", EventType::OPEN)
        .value("FILL", EventType::FILL)
        .value("CANCEL", EventType::CANCEL)
        .value("CHANGE", EventType::CHANGE)
        .value("ERROR", EventType::ERROR)
        .value("ANALYZE", EventType::ANALYZE)
        .value("HALT", EventType::HALT)
        .value("CONTINUE", EventType::CONTINUE)
        .value("EXIT", EventType::EXIT)
        .value("HEARTBEAT", EventType::HEARTBEAT);

    py::enum_<DataType>(m, "DataType", py::arithmetic())
        .value("ORDER", DataType::ORDER)
        .value("TRADE", DataType::TRADE);

    py::bind_vector<std::vector<std::string>>(m, "StringVec");
    m.attr("EventTypes") = EventType_names;
    m.attr("DataTypes") = DataType_names;

    m.def("EventType_to_string", &EventType_to_string, "EventType enum to string");
    m.def("DataType_to_string", &DataType_to_string, "DataType enum to string");
    m.def("EventType_from_string", &EventType_from_string, "string to EventType enum");
    m.def("DataType_from_string", &DataType_from_string, "string to DataType enum");

    py::enum_<ExchangeType>(m, "ExchangeType", py::arithmetic())
        .value("NONE", ExchangeType::NONE)
        .value("SYNTHETIC", ExchangeType::SYNTHETIC);

    m.attr("ExchangeTypes") = ExchangeType_names;
    m.def("ExchangeType_to_string", &ExchangeType_to_string, "ExchangeType enum to string");
    m.def("ExchangeType_from_string", &ExchangeType_from_string, "string to ExchangeType enum");

}
