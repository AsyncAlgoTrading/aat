#pragma once

#include <iostream>
#include <pybind11/pybind11.h>

#include <aat/enums.hpp>
#include <aat/order_book.hpp>

namespace py = pybind11;

PYBIND11_MODULE(binding, m) {
    m.doc() = "C++ bindings";

    /*
     * Enums
     */
    using namespace aat::config;
    py::enum_<Side>(m, "Side", py::arithmetic()).value("BUY", Side::BUY).value("SELL", Side::SELL);

    py::enum_<EventType>(m, "EventType", py::arithmetic())
        .value("TRADE", EventType::TRADE)
        .value("OPEN", EventType::OPEN)
        .value("CANCEL", EventType::CANCEL)
        .value("CHANGE", EventType::CHANGE)
        .value("FILL", EventType::FILL)
        .value("DATA", EventType::DATA)
        .value("HALT", EventType::HALT)
        .value("CONTINUE", EventType::CONTINUE)
        .value("ERROR", EventType::ERROR)
        .value("START", EventType::START)
        .value("EXIT", EventType::EXIT);

    py::enum_<DataType>(m, "DataType", py::arithmetic()).value("ORDER", DataType::ORDER).value("TRADE", DataType::TRADE);
    py::enum_<InstrumentType>(m, "InstrumentType", py::arithmetic()).value("CURRENCY", InstrumentType::CURRENCY).value("EQUITY", InstrumentType::EQUITY);

    py::enum_<OrderType>(m, "OrderType", py::arithmetic())
        .value("LIMIT", OrderType::LIMIT)
        .value("MARKET", OrderType::LIMIT)
        .value("STOP_LIMIT", OrderType::STOP_LIMIT)
        .value("STOP_MARKET", OrderType::STOP_MARKET);

    py::bind_vector<std::vector<std::string>>(m, "StringVec");
    m.attr("Sides") = Side_names;
    m.attr("EventTypes") = EventType_names;
    m.attr("DataTypes") = DataType_names;
    m.attr("InstrumentTypes") = InstrumentType_names;
    m.attr("OrderTypes") = OrderType_names;
    m.attr("OrderFlags") = OrderFlag_names;

    m.def("Side_to_string", &Side_to_string, "Side enum to string");
    m.def("EventType_to_string", &EventType_to_string, "EventType enum to string");
    m.def("DataType_to_string", &DataType_to_string, "DataType enum to string");
    m.def("InstrumentType_to_string", &InstrumentType_to_string, "InstrumentType enum to string");
    m.def("OrderType_to_string", &OrderType_to_string, "OrderType enum to string");
    m.def("OrderFlag_to_string", &OrderFlag_to_string, "OrderFlag enum to string");
    m.def("Side_from_string", &Side_from_string, "string to Side enum");
    m.def("EventType_from_string", &EventType_from_string, "string to EventType enum");
    m.def("DataType_from_string", &DataType_from_string, "string to DataType enum");
    m.def("InstrumentType_from_string", &InstrumentType_from_string, "string to InstrumentType enum");
    m.def("OrderType_from_string", &OrderType_from_string, "string to OrderType enum");
    m.def("OrderFlag_from_string", &OrderFlag_from_string, "string to OrderFlag enum");

    using namespace aat::core;
    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<const std::string&>());
    py::class_<Instrument>(m, "Instrument")
        .def(py::init<const std::string&, InstrumentType&>())
        .def("__repr__", &Instrument::toString);
}
