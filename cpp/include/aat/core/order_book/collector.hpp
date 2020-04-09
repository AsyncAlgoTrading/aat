#pragma once
#include <deque>
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
    Collector(std::function<void(Event*)> callback);

    void reset();
    void setCallback(std::function<void(Event*)> callback);
    void push(Event* event);
    void pushOpen(Order* order);
    void pushFill(Order* order, bool accumulate = false);
    void pushChange(Order* order, bool accumulate = false);
    void pushCancel(Order* order, bool accumulate = false);
    void pushTrade(Order* taker_order);
    std::uint64_t clearLevel(PriceLevel* price_level);
    void commit();
    void revert();
    void clear();
    double getPrice() const;
    double getVolume() const;
    std::deque<Order*> getOrders() const;
    std::deque<Event*> getEvents() const;
    std::deque<PriceLevel*> getPriceLevels() const;
    std::deque<PriceLevel*> getClearedLevels() const;

  private:
    void _accumulate(Order* order);

    double price;
    double volume;
    std::function<void(Event*)> callback;
    std::deque<Event*> events;
    std::deque<Order*> orders;
    std::deque<PriceLevel*> price_levels;
  };

} // namespace core
} // namespace aat
