#pragma once
#include <deque>
#include <memory>
#include <string>

#include <aat/core/order_book/price_level.hpp>
#include <aat/core/data/event.hpp>
#include <aat/core/data/order.hpp>
#include <aat/core/data/trade.hpp>

namespace aat {
namespace core {

  class PriceLevel;

  class Collector {
   public:
    Collector();
    explicit Collector(std::function<void(std::shared_ptr<Event>)> callback);

    void reset();
    void setCallback(std::function<void(std::shared_ptr<Event>)> callback);
    void push(std::shared_ptr<Event> event);
    void pushOpen(std::shared_ptr<Order> order);
    void pushFill(std::shared_ptr<Order> order, bool accumulate = false, double filled_in_txn = 0.0);
    void pushChange(std::shared_ptr<Order> order, bool accumulate = false, double filled_in_txn = 0.0);
    void pushCancel(std::shared_ptr<Order> order, bool accumulate = false, double filled_in_txn = 0.0);
    void pushTrade(std::shared_ptr<Order> taker_order, double filled_in_txn);
    std::uint64_t clearLevel(std::shared_ptr<PriceLevel> price_level);
    void commit();
    void revert();
    void clear();
    double getPrice() const;
    double getVolume() const;
    std::shared_ptr<Order> getTakerOrder() const;
    std::deque<std::shared_ptr<Order>> getOrders() const;
    std::deque<std::shared_ptr<Event>> getEvents() const;
    std::deque<std::shared_ptr<PriceLevel>> getPriceLevels() const;
    std::uint64_t getClearedLevels() const;

   private:
    void _accumulate(std::shared_ptr<Order> order, double filled_in_txn);

    std::function<void(std::shared_ptr<Event>)> callback;
    double price;
    double volume;
    std::deque<std::shared_ptr<Event>> events;
    std::shared_ptr<Order> taker_order;
    std::deque<std::shared_ptr<Order>> orders;
    std::deque<std::shared_ptr<PriceLevel>> price_levels;
  };

}  // namespace core
}  // namespace aat
