#pragma once

#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11_json/pybind11_json.hpp>

#include <aat/config/enums.hpp>
#include <aat/core/models/data.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>
#include <aat/core/models/trade.hpp>
#include <aat/core/order_book/order_book.hpp>

namespace py = pybind11;

PYBIND11_MODULE(binding, m) {
  m.doc() = "C++ bindings";

  /*
   * Enums
   */
  using namespace aat::config;
  py::enum_<Side>(m, "Side", py::arithmetic()).value("BUY", Side::BUY).value("SELL", Side::SELL).export_values();

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
    .value("EXIT", EventType::EXIT)
    .export_values();

  py::enum_<DataType>(m, "DataType", py::arithmetic())
    .value("ORDER", DataType::ORDER)
    .value("TRADE", DataType::TRADE)
    .export_values();

  py::enum_<InstrumentType>(m, "InstrumentType", py::arithmetic())
    .value("CURRENCY", InstrumentType::CURRENCY)
    .value("EQUITY", InstrumentType::EQUITY)
    .export_values();

  py::enum_<OrderType>(m, "OrderType", py::arithmetic())
    .value("LIMIT", OrderType::LIMIT)
    .value("MARKET", OrderType::MARKET)
    .value("STOP", OrderType::STOP)
    .export_values();

  py::enum_<OrderFlag>(m, "OrderFlag", py::arithmetic())
    .value("NONE", OrderFlag::NONE)
    .value("FILL_OR_KILL", OrderFlag::FILL_OR_KILL)
    .value("ALL_OR_NONE", OrderFlag::ALL_OR_NONE)
    .value("IMMEDIATE_OR_CANCEL", OrderFlag::IMMEDIATE_OR_CANCEL)
    .export_values();

  using namespace aat::core;
  py::class_<OrderBook>(m, "OrderBookCpp")
    .def(py::init<Instrument&>())
    .def(py::init<Instrument&, Exchange&>())
    .def(py::init<Instrument&, Exchange&, std::function<void(Event&)>>());

  py::class_<Exchange>(m, "ExchangeCpp")
      .def(py::init<const std::string&>())
      .def("__init__", [](py::object obj) {
          return Exchange(obj.cast<std::string>());
      })
      .def("__repr__", &Exchange::toString);

  py::class_<Instrument>(m, "InstrumentCpp")
      .def(py::init<const std::string&, InstrumentType&>())
      .def(py::init<const py::object&, InstrumentType&>())
      .def(py::init<const py::object&>())
      .def(py::init<const std::string&>())
      .def("__repr__", &Instrument::toString)
      .def("__eq__", &Instrument::operator==);

  py::class_<Data>(m, "DataCpp")
      .def(py::init<std::uint64_t, double, double, double, Side, DataType,
      Instrument, Exchange, float>()) .def("__repr__", &Data::toString)
      .def("__eq__", &Data::operator==)
      .def("__lt__", &Data::operator<)
      .def("toJson", &Data::toJson)
      .def("perspectiveSchema", &Data::perspectiveSchema);

  py::class_<Event>(m, "EventCpp")
      .def(py::init<EventType, Data>())
      .def("__repr__", &Event::toString)
      .def("toJson", &Event::toJson);

  py::class_<Order>(m, "OrderCpp")
      .def(py::init<std::uint64_t, double, double, double, Side,
      Instrument, Exchange, float, OrderType, OrderFlag, Order*, double>())
      .def("__repr__", &Order::toString)
      .def("toJson", &Order::toJson)
      .def("perspectiveSchema", &Order::perspectiveSchema);

  py::class_<Trade>(m, "TradeCpp")
      .def(py::init<std::uint64_t, double, double, double, Side,
      Instrument, Exchange, float, std::deque<Order*>, Order*>())
      .def("__repr__", &Trade::toString)
      .def("slippage", &Trade::slippage)
      .def("transactionCost", &Trade::transactionCost)
      .def("toJson", &Trade::toJson)
      .def("perspectiveSchema", &Trade::perspectiveSchema);
}
