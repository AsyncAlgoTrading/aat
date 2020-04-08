#include <aat/core/order_book/collector.hpp>

namespace aat {
namespace core {
  Collector::Collector()
    : callback([](Event& e) {}) {}
  Collector::Collector(std::function<void(Event&)> callback)
    : callback(callback) {}

  void
  Collector::reset() {}
  void
  Collector::setCallback(std::function<void(Event&)> callback) {
    this->callback = callback;
  }
  void
  Collector::push(Event& event) {}
  void
  Collector::pushOpen(Order& order) {}
  void
  Collector::pushFill(Order& order, bool accumulate) {}
  void
  Collector::pushChange(Order& order, bool accumulate) {}
  void
  Collector::pushCancel(Order& order, bool accumulate) {}
  void
  Collector::pushTrade(Order& taker_order) {}
  void
  Collector::accumulate(Order& order) {}
  void
  Collector::clearLevel(PriceLevel& price_level) {}
  void
  Collector::commit() {}
  void
  Collector::revert() {}
  void
  Collector::clear() {}
  double
  Collector::getPrice() const {
    return 0.0;
  }
  double
  Collector::getVolume() const {
    return 0.0;
  }
  std::deque<Order*>
  Collector::getOrders() const {
    return orders;
  }
  std::deque<Event*>
  Collector::getEvents() const {
    return events;
  }
  std::deque<PriceLevel*>
  Collector::getPriceLevels() const {
    return price_levels;
  }
  std::deque<PriceLevel*>
  Collector::getClearedLevels() const {}

} // namespace core
} // namespace aat
