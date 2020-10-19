#pragma once
#define AAT_PYTHON

#include <deque>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <pybind11/chrono.h>
#include <pybind11/functional.h>
#include <pybind11_json/pybind11_json.hpp>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/data/data.hpp>
#include <aat/core/data/event.hpp>
#include <aat/core/data/order.hpp>
#include <aat/core/data/trade.hpp>
#include <aat/core/position/cash.hpp>
#include <aat/core/position/position.hpp>
#include <aat/core/order_book/order_book.hpp>

namespace py = pybind11;
using namespace aat::common;

PYBIND11_MODULE(binding, m) {
  m.doc() = "C++ bindings";

  /*******************************
   * Enums
   ******************************/
  using namespace aat::config;
  py::enum_<TradingType>(m, "TradingTypeCpp", py::arithmetic())
    .value("LIVE", TradingType::LIVE)
    .value("SIMULATION", TradingType::SIMULATION)
    .value("SANDBOX", TradingType::SANDBOX)
    .value("BACKTEST", TradingType::BACKTEST)
    .export_values();

  py::enum_<Side>(m, "SideCpp", py::arithmetic()).value("BUY", Side::BUY).value("SELL", Side::SELL).export_values();

  py::enum_<EventType>(m, "EventTypeCpp", py::arithmetic())
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
    .value("BOUGHT", EventType::BOUGHT)
    .value("SOLD", EventType::SOLD)
    .value("RECEIVED", EventType::RECEIVED)
    .value("REJECTED", EventType::REJECTED)
    .value("CANCELED", EventType::CANCELED)
    .export_values();

  py::enum_<DataType>(m, "DataTypeCpp", py::arithmetic())
    .value("DATA", DataType::DATA)
    .value("ERROR", DataType::ERROR)
    .value("ORDER", DataType::ORDER)
    .value("TRADE", DataType::TRADE)
    .export_values();

  py::enum_<InstrumentType>(m, "InstrumentTypeCpp", py::arithmetic())
    .value("CURRENCY", InstrumentType::CURRENCY)
    .value("EQUITY", InstrumentType::EQUITY)
    .export_values();

  py::enum_<OrderType>(m, "OrderTypeCpp", py::arithmetic())
    .value("LIMIT", OrderType::LIMIT)
    .value("MARKET", OrderType::MARKET)
    .value("STOP", OrderType::STOP)
    .export_values();

  py::enum_<OrderFlag>(m, "OrderFlagCpp", py::arithmetic())
    .value("NONE", OrderFlag::NONE)
    .value("FILL_OR_KILL", OrderFlag::FILL_OR_KILL)
    .value("ALL_OR_NONE", OrderFlag::ALL_OR_NONE)
    .value("IMMEDIATE_OR_CANCEL", OrderFlag::IMMEDIATE_OR_CANCEL)
    .export_values();

  py::enum_<ExitRoutine>(m, "ExitRoutineCpp", py::arithmetic())
    .value("NONE", ExitRoutine::NONE)
    .value("CLOSE_ALL", ExitRoutine::CLOSE_ALL)
    .export_values();

  /*******************************
   * OrderBook
   ******************************/
  using namespace aat::core;
  py::class_<OrderBook>(m, "OrderBookCpp")
    .def(py::init<Instrument&>())
    .def(py::init<Instrument&, ExchangeType&>())
    .def(py::init<Instrument&, ExchangeType&, std::function<void(std::shared_ptr<Event>)>>())
    .def("__repr__", &OrderBook::toString)
    .def(
      "__iter__", [](const OrderBook& o) { return py::make_iterator(o.begin(), o.end()); },
      py::keep_alive<0, 1>()) /* Essential: keep object alive while iterator exists */
    .def("setCallback", &OrderBook::setCallback)
    .def("add", &OrderBook::add)
    .def("cancel", &OrderBook::cancel)
    .def("topOfBook", &OrderBook::topOfBookMap)
    .def("spread", &OrderBook::spread)
    .def("level", (std::vector<std::shared_ptr<PriceLevel>>(OrderBook::*)(double) const) & OrderBook::level)
    .def("level", (std::vector<double>(OrderBook::*)(std::uint64_t) const) & OrderBook::level)
    .def("levels", &OrderBook::levelsMap);

  /*******************************
   * PriceLevel
   ******************************/
  py::class_<PriceLevel>(m, "_PriceLevelCpp")
    .def(py::init<double, Collector&>())
    .def(
      "__iter__", [](const PriceLevel& pl) { return py::make_iterator(pl.cbegin(), pl.cend()); },
      py::keep_alive<0, 1>()) /* Essential: keep object alive while iterator exists */
    .def("__getitem__", &PriceLevel::operator[])
    .def("__bool__", &PriceLevel::operator bool)
    .def("getPrice", &PriceLevel::getPrice)
    .def("getVolume", &PriceLevel::getVolume)
    .def("add", &PriceLevel::add);

  /*******************************
   * Collector
   ******************************/
  using namespace pybind11::literals;
  py::class_<Collector>(m, "_CollectorCpp")
    .def(py::init<std::function<void(std::shared_ptr<Event>)>>())
    .def("pushOpen", &Collector::pushOpen)
    .def("pushChange", &Collector::pushChange, py::arg("order").none(false), py::arg("accumulate") = false,
      py::arg("filled_in_txn") = 0.0)
    .def("getVolume", &Collector::getVolume);

  /*******************************
   * Exchange
   ******************************/
  py::class_<ExchangeType>(m, "ExchangeTypeCpp")
    .def(py::init<const str_t&>())
    .def("__init__", [](py::object obj) { return ExchangeType(obj.cast<str_t>()); })
    .def("__repr__", &ExchangeType::toString)
    .def("__bool__", &ExchangeType::operator bool)
    .def("__eq__", &ExchangeType::operator==)
    .def_readonly("type", &ExchangeType::name);

  /*******************************
   * Instrument
   ******************************/
  py::class_<Instrument>(m, "InstrumentCpp")
    .def(py::init<const str_t&, InstrumentType&>())
    .def(py::init<const str_t&>())
    .def("__repr__", &Instrument::toString)
    .def("__eq__", &Instrument::operator==)
    .def_readonly("type", &Instrument::name)
    .def_readonly("type", &Instrument::type)
    .def_readonly("type", &Instrument::exchanges);

  /*******************************
   * Data
   ******************************/
  py::class_<Data, std::shared_ptr<Data>>(m, "DataCpp")
    .def(py::init<uint_t, timestamp_t, Instrument&, ExchangeType&>())
    .def("__repr__", &Data::toString)
    .def("__eq__", &Data::operator==)
    .def("toJson", &Data::toJson)
    .def("perspectiveSchema", &Data::perspectiveSchema)
    .def_readwrite("id", &Data::id)
    .def_readwrite("timestamp", &Data::timestamp)
    .def_readonly("type", &Data::type)
    .def_readonly("instrument", &Data::instrument)
    .def_readonly("exchange", &Data::exchange);

  py::class_<Event>(m, "EventCpp")
    .def(py::init<EventType, std::shared_ptr<Data>>(), py::arg("type").none(false),
      py::arg("target").none(true))  // allow None, convert to nullptr
    .def(py::init<EventType, std::shared_ptr<Trade>>())
    .def(py::init<EventType, std::shared_ptr<Order>>())
    .def("__repr__", &Event::toString)
    .def("toJson", &Event::toJson)
    .def_readonly("type", &Event::type)
    .def_readonly("target", &Event::target);

  py::class_<Order, std::shared_ptr<Order>>(m, "OrderCpp")
    .def(py::init<uint_t, timestamp_t, double, double, Side, Instrument&, ExchangeType&, double, OrderType, OrderFlag,
           std::shared_ptr<Order>>(),
      py::arg("id").none(false), py::arg("timestamp").none(false), py::arg("volume").none(false),
      py::arg("price").none(false), py::arg("side").none(false), py::arg("instrument").none(false),
      py::arg("exchange").none(false), py::arg("notional").none(false), py::arg("order_type").none(false),
      py::arg("flag").none(false), py::arg("stop_target").none(true))
    .def("__repr__", &Order::toString)
    .def("finished", &Order::finished)
    .def("finish", &Order::finish)
    .def("toJson", &Order::toJson)
    .def("perspectiveSchema", &Order::perspectiveSchema)
    .def_readwrite("id", &Order::id)
    .def_readwrite("timestamp", &Order::timestamp)
    .def_readwrite("volume", &Order::volume)
    .def_readwrite("price", &Order::price)
    .def_readonly("side", &Order::side)
    .def_readonly("type", &Order::type)
    .def_readonly("instrument", &Order::instrument)
    .def_readonly("exchange", &Order::exchange)
    .def_readwrite("filled", &Order::filled)
    .def_readonly("order_type", &Order::order_type)
    .def_readonly("flag", &Order::flag)
    .def_readonly("stop_target", &Order::stop_target)
    .def_readwrite("notional", &Order::notional);

  py::class_<Trade, std::shared_ptr<Trade>>(m, "TradeCpp")
    .def(py::init<uint_t, double, double, std::deque<std::shared_ptr<Order>>, std::shared_ptr<Order>>())
    .def("__repr__", &Trade::toString)
    .def("slippage", &Trade::slippage)
    .def("transactionCost", &Trade::transactionCost)
    .def("finished", &Trade::finished)
    .def("toJson", &Trade::toJson)
    .def("perspectiveSchema", &Trade::perspectiveSchema)
    .def_readwrite("id", &Trade::id)
    .def_readonly("timestamp", &Trade::timestamp)
    .def_readwrite("volume", &Trade::volume)
    .def_readwrite("price", &Trade::price)
    .def_readonly("type", &Trade::type)
    .def_readwrite("maker_orders", &Trade::maker_orders)
    .def_readwrite("taker_order", &Trade::taker_order)
    .def_readwrite("my_order", &Trade::my_order);

  /*******************************
   * Position
   ******************************/
  py::class_<Account>(m, "AccountCpp")
    .def(py::init<str_t, ExchangeType&, std::vector<std::shared_ptr<Position>>&>())
    .def("__repr__", &Account::toString)
    .def("toJson", &Account::toJson)
    .def("perspectiveSchema", &Account::perspectiveSchema);

  py::class_<Position>(m, "PositionCpp")
    .def(py::init<double, double, timestamp_t, Instrument&, ExchangeType&, std::vector<std::shared_ptr<Trade>>&>())
    .def("__repr__", &Position::toString)
    .def("toJson", &Position::toJson)
    .def("perspectiveSchema", &Position::perspectiveSchema);

  py::class_<CashPosition>(m, "CashPositionCpp")
    .def(py::init<double, timestamp_t, Instrument&, ExchangeType&>())
    .def("__repr__", &CashPosition::toString)
    .def("toJson", &CashPosition::toJson)
    .def("perspectiveSchema", &CashPosition::perspectiveSchema);

  /*******************************
   * Helpers
   ******************************/
  // NONE
}
