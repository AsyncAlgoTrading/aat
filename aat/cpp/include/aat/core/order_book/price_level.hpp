#pragma once
#include <deque>
#include <memory>
#include <string>
#include <vector>

#include <aat/core/order_book/collector.hpp>
#include <aat/core/data/event.hpp>
#include <aat/core/data/order.hpp>

namespace aat {
namespace core {

  class Collector;

  class PriceLevel {
   public:
    PriceLevel(double price, Collector& collector);  // NOLINT

    double
    getPrice() const {
      return price;
    }
    double getVolume() const;

    void add(std::shared_ptr<Order> order);
    std::shared_ptr<Order> find(std::shared_ptr<Order> order);
    std::shared_ptr<Order> remove(std::shared_ptr<Order> order);
    std::shared_ptr<Order> modify(std::shared_ptr<Order> order);
    std::shared_ptr<Order> cross(
      std::shared_ptr<Order> taker_order, std::vector<std::shared_ptr<Order>>& secondaries);  // NOLINT

    void clear();
    void commit();
    void revert();

    std::uint64_t
    size() const {
      return orders.size();
    }

    std::shared_ptr<Order> operator[](int i) { return orders[i]; }
    explicit operator bool() const { return orders.size() > 0; }
    using iterator = std::deque<std::shared_ptr<Order>>::iterator;
    using const_iterator = std::deque<std::shared_ptr<Order>>::const_iterator;

    iterator
    begin() noexcept {
      return orders.begin();
    }
    const_iterator
    cbegin() const noexcept {
      return orders.cbegin();
    }
    iterator
    end() noexcept {
      return orders.end();
    }
    const_iterator
    cend() const noexcept {
      return orders.cend();
    }

   private:
    double price;
    Collector& collector;
    std::deque<std::shared_ptr<Order>> orders{};
    std::deque<std::shared_ptr<Order>> orders_staged;
    std::deque<double> orders_filled_staged;
    std::vector<std::shared_ptr<Order>> stop_orders;
    std::vector<std::shared_ptr<Order>> stop_orders_staged;
  };
}  // namespace core
}  // namespace aat
