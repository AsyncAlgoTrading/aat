#pragma once
#include <deque>
#include <memory>
#include <string>
#include <pybind11/pybind11.h>
#include <aat/core/order_book/price_level.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>
#include <aat/core/models/trade.hpp>

namespace py = pybind11;

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
    void pushFill(std::shared_ptr<Order> order, bool accumulate = false);
    void pushChange(std::shared_ptr<Order> order, bool accumulate = false);
    void pushCancel(std::shared_ptr<Order> order, bool accumulate = false);
    void pushTrade(std::shared_ptr<Order> taker_order);
    std::uint64_t clearLevel(std::shared_ptr<PriceLevel> price_level);
    void commit();
    void revert();
    void clear();
    double getPrice() const;
    double getVolume() const;
    std::deque<std::shared_ptr<Order>> getOrders() const;
    std::deque<std::shared_ptr<Event>> getEvents() const;
    std::deque<std::shared_ptr<PriceLevel>> getPriceLevels() const;
    std::uint64_t getClearedLevels() const;

   private:
    void _accumulate(std::shared_ptr<Order> order);

    double price;
    double volume;
    std::function<void(std::shared_ptr<Event>)> callback;
    std::deque<std::shared_ptr<Event>> events;
    std::deque<std::shared_ptr<Order>> orders;
    std::deque<std::shared_ptr<PriceLevel>> price_levels;
  };

}  // namespace core
}  // namespace aat
