#pragma once

#include <aat/common.hpp>
#include <aat/config/enums.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {

  class Instrument {
   public:
    explicit Instrument(const py::object& name)
      : name(name.cast<str_t>())
      , type(InstrumentType::EQUITY) {}

    Instrument(const py::object& name, InstrumentType type)
      : name(name.cast<str_t>())
      , type(type) {}

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
