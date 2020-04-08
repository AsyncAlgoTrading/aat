#pragma once

#include <iostream>
#include <unordered_map>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include <aat/common.hpp>

namespace py = pybind11;
PYBIND11_MAKE_OPAQUE(std::vector<std::string>);

namespace aat {
namespace config {
  enum class Side { NONE = 0, BUY = 1, SELL = 2 };

  enum class EventType {
    TRADE = 1,
    OPEN = 2,
    CANCEL = 3,
    CHANGE = 4,
    FILL = 5,
    DATA = 6,
    HALT = 7,
    CONTINUE = 8,
    ERROR = 9,
    START = 10,
    EXIT = 11
  };

  enum class DataType {
    ORDER = 1,
    TRADE = 2,
  };

  enum class InstrumentType {
    CURRENCY = 1,
    EQUITY = 2,
  };

  enum class OrderType {
    LIMIT = 0,
    MARKET = 1,
    STOP = 2,
  };

  enum class OrderFlag {
    NONE = 0,
    FILL_OR_KILL = 1,
    ALL_OR_NONE = 2,
    IMMEDIATE_OR_CANCEL = 3,
  };

  static const std::vector<std::string> Side_names = {
    "BUY",
    "SELL",
  };

  static const std::vector<std::string> EventType_names = {
    "TRADE",
    "OPEN",
    "CANCEL",
    "CHANGE",
    "FILL",
    "DATA",
    "HALT",
    "CONTINUE",
    "ERROR",
    "START",
    "EXIT",
  };

  static const std::vector<std::string> DataType_names = {
    "ORDER",
    "TRADE",
  };

  static const std::vector<std::string> InstrumentType_names = {
    "CURRENCY",
    "EQUITY",
  };

  static const std::vector<std::string> OrderType_names = {
    "LIMIT",
    "MARKET",
    "STOP",
  };

  static const std::vector<std::string> OrderFlag_names = {
    "NONE",
    "FILL_OR_KILL",
    "ALL_OR_NONE",
    "IMMEDIATE_OR_CANCEL",
  };

  static std::unordered_map<std::string, Side> _Side_mapping = {
    {"BUY", Side::BUY},
    {"SELL", Side::SELL},
  };

  static std::unordered_map<std::string, EventType> _EventType_mapping = {
    {"TRADE", EventType::TRADE},
    {"OPEN", EventType::OPEN},
    {"CANCEL", EventType::CANCEL},
    {"CHANGE", EventType::CHANGE},
    {"FILL", EventType::FILL},
    {"DATA", EventType::DATA},
    {"HALT", EventType::HALT},
    {"CONTINUE", EventType::CONTINUE},
    {"ERROR", EventType::ERROR},
    {"START", EventType::START},
    {"EXIT", EventType::EXIT},
  };

  static std::unordered_map<std::string, DataType> _DataType_mapping = {
    {"ORDER", DataType::ORDER},
    {"TRADE", DataType::TRADE},
  };

  static std::unordered_map<std::string, InstrumentType> _InstrumentType_mapping = {
    {"CURRENCY", InstrumentType::CURRENCY},
    {"EQUITY", InstrumentType::EQUITY},
  };

  static std::unordered_map<std::string, OrderType> _OrderType_mapping = {
    {"LIMIT", OrderType::LIMIT},
    {"MARKET", OrderType::MARKET},
    {"STOP", OrderType::STOP},
  };

  static std::unordered_map<std::string, OrderFlag> _OrderFlag_mapping = {
    {"NONE", OrderFlag::NONE},
    {"FILL_OR_KILL", OrderFlag::FILL_OR_KILL},
    {"ALL_OR_NONE", OrderFlag::ALL_OR_NONE},
    {"IMMEDIATE_OR_CANCEL", OrderFlag::IMMEDIATE_OR_CANCEL},
  };

  ENUM_TO_STRING(Side)
  ENUM_TO_STRING(EventType)
  ENUM_TO_STRING(DataType)
  ENUM_TO_STRING(InstrumentType)
  ENUM_TO_STRING(OrderType)
  ENUM_TO_STRING(OrderFlag)
  ENUM_FROM_STRING(Side)
  ENUM_FROM_STRING(EventType)
  ENUM_FROM_STRING(DataType)
  ENUM_FROM_STRING(InstrumentType)
  ENUM_FROM_STRING(OrderType)
  ENUM_FROM_STRING(OrderFlag)
} // namespace config
} // namespace aat
