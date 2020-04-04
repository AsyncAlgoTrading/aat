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
