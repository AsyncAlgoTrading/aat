#pragma once

#include <vector>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/exchange/exchange.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {

  struct Instrument {
    Instrument(const str_t& name, InstrumentType type, ExchangeType exchange = NullExchange)
      : name(name)
      , type(type) {}

    explicit Instrument(const str_t& name)
      : name(name)
      , type(InstrumentType::EQUITY) {}

    bool operator==(const Instrument& other) const;
    str_t toString() const;

    str_t name;
    InstrumentType type;
    std::vector<ExchangeType> exchanges;
  };

}  // namespace core
}  // namespace aat
