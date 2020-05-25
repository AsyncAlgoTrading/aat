#include <aat/common.hpp>
#include <aat/core/order_book/collector.hpp>

using namespace aat::common;

namespace aat {
namespace core {
  Collector::Collector()
    : callback(nullptr)
    , price(0.0)
    , volume(0.0) {}

  Collector::Collector(std::function<void(Event*)> callback)
    : callback(callback)
    , price(0.0)
    , volume(0.0) {}

  void
  Collector::reset() {
    events.clear();
    price = 0.0;
    volume = 0.0;
    orders.clear();
    price_levels.clear();
  }

  void
  Collector::setCallback(std::function<void(Event*)> callback) {
    this->callback = callback;
  }

  void
  Collector::push(Event* event) {
    events.push_back(event);
  }

  void
  Collector::pushOpen(Order* order) {
    push(new Event(EventType::OPEN, order));
  }

  void
  Collector::pushFill(Order* order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(new Event(EventType::FILL, order));
  }

  void
  Collector::pushChange(Order* order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(new Event(EventType::CHANGE, order));
  }

  void
  Collector::pushCancel(Order* order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(new Event(EventType::CANCEL, order));
  }

  void
  Collector::pushTrade(Order* taker_order) {
    if (orders.size() == 0) {
      throw AATCPPException("No maker orders provied!");
    }

    if (taker_order->filled <= 0) {
      throw AATCPPException("No Trade occurred");
    }

    push(new Event(EventType::TRADE,
      new Trade(0, datetime::now(), volume, price, taker_order->side, taker_order->instrument, taker_order->exchange,
        taker_order->filled, orders, taker_order)));
  }

  void
  Collector::_accumulate(Order* order) {
    price = (volume + order->filled > 0) ? ((price * volume + order->price * order->filled) / (volume + order->filled))
                                         : 0.0;
    volume += order->filled;
    orders.push_back(order);
  }

  std::uint64_t
  Collector::clearLevel(PriceLevel* price_level) {
    price_levels.push_back(price_level);
    return price_level->size();
  }

  void
  Collector::commit() {
    // flush the event queue
    while (events.size()) {
      Event* ev = events.front();
      events.pop_front();
      if (callback)
        callback(ev);
    }

    for (PriceLevel* pl : price_levels)
      pl->commit();

    reset();
  }

  void
  Collector::revert() {
    for (PriceLevel* pl : price_levels)
      pl->revert();
    reset();
  }

  void
  Collector::clear() {
    reset();
  }

  double
  Collector::getPrice() const {
    return price;
  }

  double
  Collector::getVolume() const {
    return volume;
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

  std::uint64_t
  Collector::getClearedLevels() const {
    return price_levels.size();
  }

}  // namespace core
}  // namespace aat
