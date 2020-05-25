#pragma once

#include <stdint.h>
#include <string>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>

using json = nlohmann::json;
using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {

  class ExchangeType {
   public:
    explicit ExchangeType(str_t name)
      : name(name) {}

    str_t toString() const;

   private:
    str_t name;
  };

  static ExchangeType NullExchange = ExchangeType("");

}  // namespace core
}  // namespace aat
