#pragma once

#include <stdint.h>
#include <string>
#include <deque>

#include <nlohmann/json.hpp>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>

using json = nlohmann::json;
using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {

  struct ExchangeType {
    explicit ExchangeType(str_t name)
      : name(name) {}

    str_t toString() const;
    virtual json toJson() const;

    bool
    operator==(const ExchangeType& other) const {
      return name == other.name;
    }
    explicit operator bool() const { return name != ""; }
    str_t name;
  };


  static ExchangeType NullExchange = ExchangeType("");

}  // namespace core
}  // namespace aat
