#pragma once
#include <deque>
#include <string>
#include <pybind11/pybind11.h>

#include <aat/core/order_book/collector.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

namespace py = pybind11;

namespace aat {
namespace core {

  class Collector;

  class PriceLevel {
  public:
    PriceLevel(double price, Collector& collector);

    double
    getPrice() const {
      return price;
    }
    double getVolume() const;

    void add(Order* order);
    Order* remove(Order* order);
    Order* cross(Order* taker_order, std::vector<Order*>& secondaries);

    void clear();
    void commit();
    void revert();

    std::uint64_t
    size() const {
      return orders.size();
    }

  private:
    double price;
    Collector& collector;
    std::deque<Order*> orders{};
    std::deque<Order*> orders_staged;
    std::vector<Order*> stop_orders;
    std::vector<Order*> stop_orders_staged;
  };
} // namespace core
} // namespace aat
