#pragma once

#include <deque>
#include <date.h>
#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/exchange/exchange.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  struct Data {
   public:
    Data(uint_t id, double volume, double price, Side side, DataType type, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0)
      : id(id)
      , timestamp(datetime::now())
      , volume(volume)
      , price(price)
      , side(side)
      , type(type)
      , instrument(instrument)
      , exchange(exchange)
      , filled(filled) {}

    Data(uint_t id, timestamp_t timestamp, double volume, double price, Side side, DataType type, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0)
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
    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    uint_t id;
    timestamp_t timestamp;
    double volume;
    double price;
    Side side;
    DataType type;
    Instrument instrument;
    ExchangeType exchange;
    double filled;
  };

}  // namespace core
}  // namespace aat
