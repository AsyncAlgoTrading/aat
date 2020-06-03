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
  struct Order : public Data {
    Order(uint_t id, timestamp_t timestamp, double volume, double price, Side side, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0, OrderType order_type = OrderType::LIMIT,
      OrderFlag flag = OrderFlag::NONE, std::shared_ptr<Order> stop_target = nullptr, double notional = 0.0);

    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    const OrderType order_type = OrderType::LIMIT;
    const OrderFlag flag = OrderFlag::NONE;
    const std::shared_ptr<Order> stop_target = nullptr;
    double notional = 0.0;
  };

}  // namespace core
}  // namespace aat
