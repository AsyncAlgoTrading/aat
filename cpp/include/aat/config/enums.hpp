#pragma once

#include <iostream>
#include <unordered_map>
#include <vector>

#include <aat/common.hpp>

using namespace aat::common;

namespace aat {
namespace config {

  enum class Side { NONE = 0, BUY = 1, SELL = 2 };

  enum class EventType {
    TRADE = 0,
    OPEN = 1,
    CANCEL = 2,
    CHANGE = 3,
    FILL = 4,
    DATA = 5,
    HALT = 6,
    CONTINUE = 7,
    ERROR = 8,
    START = 9,
    EXIT = 10
  };

  enum class DataType {
    ORDER = 0,
    TRADE = 1,
  };

  enum class InstrumentType {
    CURRENCY = 0,
    EQUITY = 1,
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

  static const std::vector<str_t> Side_names = {
    "BUY",
    "SELL",
  };

  static const std::vector<str_t> EventType_names = {
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

  static const std::vector<str_t> DataType_names = {
    "ORDER",
    "TRADE",
  };

  static const std::vector<str_t> InstrumentType_names = {
    "CURRENCY",
    "EQUITY",
  };

  static const std::vector<str_t> OrderType_names = {
    "LIMIT",
    "MARKET",
    "STOP",
  };

  static const std::vector<str_t> OrderFlag_names = {
    "NONE",
    "FILL_OR_KILL",
    "ALL_OR_NONE",
    "IMMEDIATE_OR_CANCEL",
  };

  static std::unordered_map<str_t, Side> _Side_mapping = {
    {"BUY", Side::BUY},
    {"SELL", Side::SELL},
  };

  static std::unordered_map<str_t, EventType> _EventType_mapping = {
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

  static std::unordered_map<str_t, DataType> _DataType_mapping = {
    {"ORDER", DataType::ORDER},
    {"TRADE", DataType::TRADE},
  };

  static std::unordered_map<str_t, InstrumentType> _InstrumentType_mapping = {
    {"CURRENCY", InstrumentType::CURRENCY},
    {"EQUITY", InstrumentType::EQUITY},
  };

  static std::unordered_map<str_t, OrderType> _OrderType_mapping = {
    {"LIMIT", OrderType::LIMIT},
    {"MARKET", OrderType::MARKET},
    {"STOP", OrderType::STOP},
  };

  static std::unordered_map<str_t, OrderFlag> _OrderFlag_mapping = {
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
}  // namespace config
}  // namespace aat
