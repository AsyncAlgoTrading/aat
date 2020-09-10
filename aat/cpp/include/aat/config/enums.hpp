#pragma once

#include <iostream>
#include <unordered_map>
#include <vector>

#include <aat/common.hpp>

using namespace aat::common;

namespace aat {
namespace config {

  enum class TradingType {
    LIVE = 0,
    SIMULATION = 1,
    SANDBOX = 2,
    BACKTEST = 3,
  };

  enum class Side {
    NONE = 0,
    BUY = 1,
    SELL = 2,
  };

  enum class OptionType {
    CALL = 0,
    PUT = 0,
  };

  enum class EventType {
    // Heartbeat events
    HEARTBEAT = 0,

    // Trade events
    TRADE = 1,

    // Order events
    OPEN = 2,
    CANCEL = 3,
    CHANGE = 4,
    FILL = 5,

    // Other data events
    DATA = 6,

    // System events
    HALT = 7,
    CONTINUE = 8,

    // Engine events
    ERROR = 9,
    START = 10,
    EXIT = 11,

    // Order Events
    BOUGHT = 12,
    SOLD = 13,
    REJECTED = 14,
    CANCELED = 15
  };

  enum class DataType {
    DATA = 0,
    ERROR = 1,
    ORDER = 2,
    TRADE = 3,
  };

  enum class InstrumentType {
    OTHER = 0,
    EQUITY = 1,
    BOND = 2,
    OPTION = 3,
    FUTURE = 4,
    PAIR = 6,
    SPREAD = 7,
    FUTURESOPTION = 8,
    MUTUALFUND = 9,
    COMMODITY = 10,
    CURRENCY = 11,
    INDEX = 12,
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

  static const std::vector<str_t> TradingType_names = {
    "LIVE",
    "SIMULATION",
    "SANDBOX",
    "BACKTEST",
  };

  static const std::vector<str_t> Side_names = {
    "NONE",
    "BUY",
    "SELL",
  };

  static const std::vector<str_t> OptionType_names = {
    "CALL",
    "PUT",
  };

  static const std::vector<str_t> EventType_names = {
    "HEARTBEAT",
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
    "BOUGHT",
    "SOLD",
    "REJECTED",
    "CANCELED",
  };

  static const std::vector<str_t> DataType_names = {
    "DATA",
    "ERROR",
    "ORDER",
    "TRADE",
  };

  static const std::vector<str_t> InstrumentType_names = {
    "OTHER",
    "EQUITY",
    "BOND",
    "OPTION",
    "FUTURE",
    "PAIR",
    "SPREAD",
    "FUTURESOPTION",
    "MUTUALFUND",
    "COMMODITY",
    "CURRENCY",
    "INDEX",
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

  static std::unordered_map<str_t, TradingType> _TradingType_mapping = {
    {"LIVE", TradingType::LIVE},
    {"SIMULATION", TradingType::SIMULATION},
    {"SANDBOX", TradingType::SANDBOX},
    {"BACKTEST", TradingType::BACKTEST},
  };

  static std::unordered_map<str_t, Side> _Side_mapping = {
    {"NONE", Side::NONE},
    {"BUY", Side::BUY},
    {"SELL", Side::SELL},
  };

  static std::unordered_map<str_t, OptionType> _OptionType_mapping = {
    {"CALL", OptionType::CALL},
    {"PUT", OptionType::PUT},
  };

  static std::unordered_map<str_t, EventType> _EventType_mapping = {
    {"HEARTBEAT", EventType::HEARTBEAT},
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
    {"BOUGHT", EventType::BOUGHT},
    {"SOLD", EventType::SOLD},
    {"REJECTED", EventType::REJECTED},
    {"CANCELED", EventType::CANCELED},
  };

  static std::unordered_map<str_t, DataType> _DataType_mapping = {
    {"DATA", DataType::DATA},
    {"ERROR", DataType::ERROR},
    {"ORDER", DataType::ORDER},
    {"TRADE", DataType::TRADE},
  };

  static std::unordered_map<str_t, InstrumentType> _InstrumentType_mapping = {
    {"OTHER", InstrumentType::OTHER},
    {"EQUITY", InstrumentType::EQUITY},
    {"BOND", InstrumentType::BOND},
    {"OPTION", InstrumentType::OPTION},
    {"FUTURE", InstrumentType::FUTURE},
    {"PAIR", InstrumentType::PAIR},
    {"SPREAD", InstrumentType::SPREAD},
    {"FUTURESOPTION", InstrumentType::FUTURESOPTION},
    {"MUTUALFUND", InstrumentType::MUTUALFUND},
    {"COMMODITY", InstrumentType::COMMODITY},
    {"CURRENCY", InstrumentType::CURRENCY},
    {"INDEX", InstrumentType::INDEX},
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

  ENUM_TO_STRING(TradingType)
  ENUM_TO_STRING(Side)
  ENUM_TO_STRING(OptionType)
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
