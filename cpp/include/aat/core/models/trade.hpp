#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>
#include <aat/core/models/data.hpp>
#include <aat/core/models/order.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {
  struct Trade : public Data {
    Trade(std::uint64_t id, double timestamp, double volume, double price, Side side, Instrument instrument,
      Exchange exchange = NullExchange, float filled = 0.0, std::deque<Order*> maker_orders = std::deque<Order*>(),
      Order* taker_order = nullptr)
      : Data(id, timestamp, volume, price, side, DataType::TRADE, instrument, exchange, filled)
      , maker_orders(maker_orders)
      , taker_order(taker_order)
      , _slippage(0.0)
      , _transaction_cost(0.0) {
      // enforce that stop target match stop type
      assert(maker_orders.length > 0);
    }

    double
    slippage() const {
      return 0.0;
    }
    double
    transactionCost() const {
      return 0.0;
    }
    std::string toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    std::deque<Order*> maker_orders;
    Order* taker_order;
    double _slippage;
    double _transaction_cost;
  };

} // namespace core
} // namespace aat
