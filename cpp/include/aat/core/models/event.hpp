#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>
#include <aat/core/models/data.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {
  class Event {
  public:
    Event(EventType type, Data target)
      : type(type)
      , target(target) {}

    std::string toString() const;
    json toJson() const;

  protected:
    EventType type;
    Data target;
  };

} // namespace core
} // namespace aat
