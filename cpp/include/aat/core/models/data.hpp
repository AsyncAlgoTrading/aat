#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>
#include <aat/core/exchange.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {
  struct Data {
  public:
    Data(std::uint64_t id, double timestamp, double volume, double price, Side side, DataType type,
      Instrument instrument, ExchangeType exchange = NullExchange, double filled = 0.0)
      : id(id)
      , timestamp(timestamp)
      , volume(volume)
      , price(price)
      , side(side)
      , type(type)
      , instrument(instrument)
      , exchange(exchange)
      , filled(filled) {}

    bool operator==(const Data& other);
    bool operator<(const Data& other);
    std::string toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    std::uint64_t id;
    double timestamp;
    double volume;
    double price;
    Side side;
    DataType type;
    Instrument instrument;
    ExchangeType exchange;
    double filled;
  };

} // namespace core
} // namespace aat
