#pragma once

#include <iostream>
#include <pybind11/pybind11.h>

#include <aat/enums.hpp>
#include <aat/order_book.hpp>

namespace py = pybind11;

PYBIND11_MODULE(binding, m)
{
    m.doc() = "C++ bindings";

    using namespace aat::config;
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

    using namespace aat::core;
    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<const std::string &>())
    ;
}
