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
  struct _EventTarget {
    virtual ~_EventTarget() {}
    virtual str_t toString() const = 0;
    virtual json toJson() const = 0;
    virtual json perspectiveSchema() const = 0;
  };

  struct Data : public _EventTarget {
   public:
    Data(uint_t id, Instrument instrument, ExchangeType exchange = NullExchange)
      : id(id)
      , timestamp(datetime::now())
      , type(DataType::DATA)
      , instrument(instrument)
      , exchange(exchange)
      , data(nullptr) {}

    Data(uint_t id, timestamp_t timestamp, Instrument instrument, ExchangeType exchange = NullExchange)
      : id(id)
      , timestamp(timestamp)
      , type(DataType::DATA)
      , instrument(instrument)
      , exchange(exchange)
      , data(nullptr) {}

    bool operator==(const Data& other);
    virtual str_t toString() const;
    virtual json toJson() const;
    virtual json perspectiveSchema() const;

    uint_t id;
    timestamp_t timestamp;
    const DataType type;
    const Instrument instrument;
    const ExchangeType exchange;
    void* data;
  };

}  // namespace core
}  // namespace aat
