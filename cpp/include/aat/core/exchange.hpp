#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {

  class Exchange {
  public:
    Exchange(std::string name)
      : name(name) {}

    std::string toString() const;


  private:
    std::string name;
  };

  static Exchange NullExchange = Exchange("");

} // namespace core
} // namespace aat
