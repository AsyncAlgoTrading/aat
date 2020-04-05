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

    py::enum_<OrderFlag>(m, "OrderFlag", py::arithmetic())
        .value("NONE", OrderFlag::NONE)
        .value("FILL_OR_KILL", OrderFlag::FILL_OR_KILL)
        .value("ALL_OR_NONE", OrderFlag::ALL_OR_NONE)
        .value("IMMEDIATE_OR_CANCEL", OrderFlag::IMMEDIATE_OR_CANCEL);

    using namespace aat::core;
    py::class_<OrderBook>(m, "OrderBook").def(py::init<const std::string&>());
    py::class_<Instrument>(m, "Instrument").def(py::init<const std::string&, InstrumentType&>()).def("__repr__", &Instrument::toString);
}
