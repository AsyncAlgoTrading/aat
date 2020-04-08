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
  class Data {
  public:
    Data(std::uint64_t id, double timestamp, double volume, double price, Side side, DataType type,
      Instrument instrument, Exchange exchange = Exchange(), float filled = 0.0)
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

  protected:
    std::uint64_t id;
    double timestamp;
    double volume;
    double price;
    Side side;
    DataType type;
    Instrument instrument;
    Exchange exchange;
    float filled;
  };

} // namespace core
} // namespace aat
