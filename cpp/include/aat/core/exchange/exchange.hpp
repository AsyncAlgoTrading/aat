#pragma once

#include <stdint.h>
#include <string>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>

// for convenience
using json = nlohmann::json;
using aat::config;

namespace aat {
namespace core {

  class ExchangeType {
   public:
    explicit ExchangeType(std::string name)
      : name(name) {}

    std::string toString() const;

   private:
    std::string name;
  };

  static ExchangeType NullExchange = ExchangeType("");

}  // namespace core
}  // namespace aat
