#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>
#include <aat/core/models/data.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {
  struct Order : public Data {
    Order(std::uint64_t id, double timestamp, double volume, double price, Side side, Instrument instrument,
      Exchange exchange = NullExchange, float filled = 0.0, OrderType order_type = OrderType::LIMIT,
      OrderFlag flag = OrderFlag::NONE, Order* stop_target = nullptr, double notional = 0.0);

    std::string toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    OrderType order_type = OrderType::LIMIT;
    OrderFlag flag = OrderFlag::NONE;
    Order* stop_target = nullptr;
    double notional = 0.0;
  };

} // namespace core
} // namespace aat
