#pragma once

#include <deque>
#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/models/data.hpp>
#include <aat/core/models/order.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  struct Trade : public Data {
    Trade(double volume, double price, Side side, Instrument instrument, ExchangeType exchange = NullExchange,
      double filled = 0.0, std::deque<Order*> maker_orders = std::deque<Order*>(), Order* taker_order = nullptr)
      : Trade(0, datetime::now(), volume, price, side, instrument, exchange, filled, maker_orders, taker_order) {}

    Trade(uint_t id, double volume, double price, Side side, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0, std::deque<Order*> maker_orders = std::deque<Order*>(),
      Order* taker_order = nullptr)
      : Trade(id, datetime::now(), volume, price, side, instrument, exchange, filled, maker_orders, taker_order) {}

    Trade(timestamp_t timestamp, double volume, double price, Side side, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0, std::deque<Order*> maker_orders = std::deque<Order*>(),
      Order* taker_order = nullptr)
      : Trade(0, timestamp, volume, price, side, instrument, exchange, filled, maker_orders, taker_order) {}

    Trade(uint_t id, timestamp_t timestamp, double volume, double price, Side side, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0, std::deque<Order*> maker_orders = std::deque<Order*>(),
      Order* taker_order = nullptr)
      : Data(id, timestamp, volume, price, side, DataType::TRADE, instrument, exchange, filled)
      , maker_orders(maker_orders)
      , taker_order(taker_order)
      , _slippage(0.0)
      , _transaction_cost(0.0) {
      // enforce that stop target match stop type
      assert(maker_orders.size() > 0);
    }

    double
    slippage() const {
      return 0.0;
    }
    double
    transactionCost() const {
      return 0.0;
    }
    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    std::deque<Order*> maker_orders;
    Order* taker_order;
    double _slippage;
    double _transaction_cost;
  };

}  // namespace core
}  // namespace aat
