#pragma once

#include <aat/common.hpp>
#include <aat/config/enums.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {

  class Instrument {
   public:
    Instrument(const str_t& name, InstrumentType type)
      : name(name)
      , type(type) {}

    explicit Instrument(const str_t& name)
      : name(name)
      , type(InstrumentType::EQUITY) {}

    bool operator==(const Instrument& other) const;
    str_t toString() const;

   private:
    str_t name;
    InstrumentType type;
  };

}  // namespace core
}  // namespace aat
