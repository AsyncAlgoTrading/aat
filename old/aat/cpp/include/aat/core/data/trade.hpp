#pragma once

#include <deque>
#include <memory>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/data/data.hpp>
#include <aat/core/data/order.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  struct Trade : public _EventTarget {
    Trade(str_t id, double volume, double price,
      std::deque<std::shared_ptr<Order>> maker_orders = std::deque<std::shared_ptr<Order>>(),
      std::shared_ptr<Order> taker_order = nullptr)
      : id(id)
      , timestamp(taker_order->timestamp)
      , type(DataType::TRADE)
      , volume(volume)
      , price(price)
      , maker_orders(maker_orders)
      , taker_order(taker_order)
      , my_order(nullptr)
      , _slippage(0.0)
      , _transaction_cost(0.0) {
      // enforce that stop target match stop type
      // assert(maker_orders.size() > 0);  // not necessarily
    }

    double
    slippage() const {
      return 0.0;
    }

    double
    transactionCost() const {
      return 0.0;
    }

    bool finished() const;

    virtual str_t toString() const;
    virtual json toJson() const;
    virtual json perspectiveSchema() const;

    str_t id;
    timestamp_t timestamp;
    const DataType type;

    double volume;
    double price;

    std::deque<std::shared_ptr<Order>> maker_orders;
    std::shared_ptr<Order> taker_order;
    std::shared_ptr<Order> my_order;  // FIXME

    double _slippage;
    double _transaction_cost;
  };

}  // namespace core
}  // namespace aat
