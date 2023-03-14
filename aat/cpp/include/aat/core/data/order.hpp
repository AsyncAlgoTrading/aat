#pragma once

#include <deque>
#include <memory>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/data/data.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  struct Order : public _EventTarget {
    Order(str_t id, timestamp_t timestamp, double volume, double price, Side side, Instrument& instrument,
      ExchangeType& exchange = NullExchange, double notional = 0.0, OrderType order_type = OrderType::MARKET,
      OrderFlag flag = OrderFlag::NONE, std::shared_ptr<Order> stop_target = nullptr);
    virtual ~Order() {}

    virtual bool operator==(Order& other) const;

    bool finished() const;
    void finish();

    virtual str_t toString() const;
    virtual json toJson() const;
    virtual json perspectiveSchema() const;

    str_t id;
    timestamp_t timestamp;
    const DataType type;
    const Instrument instrument;
    const ExchangeType exchange;

    double volume;
    double price;
    const Side side;

    const OrderType order_type = OrderType::MARKET;
    const OrderFlag flag = OrderFlag::NONE;
    const std::shared_ptr<Order> stop_target = nullptr;
    double notional = 0.0;

    double filled = 0.0;
    bool force_done = false;
  };

}  // namespace core
}  // namespace aat
