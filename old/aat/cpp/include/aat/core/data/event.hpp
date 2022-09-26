#pragma once

#include <deque>
#include <memory>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/data/data.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class Event {
   public:
    Event(EventType type, std::shared_ptr<_EventTarget> target)
      : type(type)
      , target(target) {}

    str_t toString() const;
    json toJson() const;

    const EventType type;
    std::shared_ptr<_EventTarget> target;
  };

}  // namespace core
}  // namespace aat
