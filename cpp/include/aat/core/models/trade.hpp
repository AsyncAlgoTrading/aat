#pragma once

#include <deque>
#include <memory>

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
    Trade(uint_t id, timestamp_t timestamp, double volume, double price, Side side, Instrument instrument,
      ExchangeType exchange = NullExchange, double filled = 0.0,
      std::deque<std::shared_ptr<Order>> maker_orders = std::deque<std::shared_ptr<Order>>(),
      std::shared_ptr<Order> taker_order = nullptr)
      : Data(id, timestamp, volume, price, side, DataType::TRADE, instrument, exchange, filled)
      , maker_orders(maker_orders)
      , taker_order(taker_order)
      , my_order(nullptr)
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

    std::deque<std::shared_ptr<Order>> maker_orders;
    std::shared_ptr<Order> taker_order;
    std::shared_ptr<Order> my_order;  // FIXME

    double _slippage;
    double _transaction_cost;
  };

}  // namespace core
}  // namespace aat
