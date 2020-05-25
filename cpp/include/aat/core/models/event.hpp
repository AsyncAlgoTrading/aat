#pragma once

#include <deque>
#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/models/data.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class Event {
   public:
    Event(EventType type, Data* target)
      : type(type)
      , target(target) {}

    str_t toString() const;
    json toJson() const;

   protected:
    EventType type;
    Data* target;
  };

}  // namespace core
}  // namespace aat
