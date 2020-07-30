#include <aat/common.hpp>
#include <aat/core/order_book/collector.hpp>

using namespace aat::common;

namespace aat {
namespace core {
  Collector::Collector()
    : callback(nullptr)
    , price(0.0)
    , volume(0.0) {}

  Collector::Collector(std::function<void(std::shared_ptr<Event>)> callback)
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
    taker_order = nullptr;
  }

  void
  Collector::setCallback(std::function<void(std::shared_ptr<Event>)> callback) {
    this->callback = callback;
  }

  void
  Collector::push(std::shared_ptr<Event> event) {
    events.push_back(event);
  }

  void
  Collector::pushOpen(std::shared_ptr<Order> order) {
    push(std::make_shared<Event>(EventType::OPEN, order));
  }

  void
  Collector::pushFill(std::shared_ptr<Order> order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(std::make_shared<Event>(EventType::FILL, order));
  }

  void
  Collector::pushChange(std::shared_ptr<Order> order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(std::make_shared<Event>(EventType::CHANGE, order));
  }

  void
  Collector::pushCancel(std::shared_ptr<Order> order, bool accumulate) {
    if (accumulate) {
      _accumulate(order);
    }
    push(std::make_shared<Event>(EventType::CANCEL, order));
  }

  void
  Collector::pushTrade(std::shared_ptr<Order> taker_order) {
    if (orders.size() == 0) {
      throw AATCPPException("No maker orders provied!");
    }

    if (taker_order->filled <= 0) {
      throw AATCPPException("No Trade occurred");
    }

    if (taker_order->volume < volume) {
      throw AATCPPException("Accumulation error occurred");
    }

    push(std::make_shared<Event>(EventType::TRADE, std::make_shared<Trade>(0, price, volume, orders, taker_order)));
    this->taker_order = taker_order;
  }

  void
  Collector::_accumulate(std::shared_ptr<Order> order) {
    price = (volume + order->filled > 0) ? ((price * volume + order->price * order->filled) / (volume + order->filled))
                                         : 0.0;
    volume += order->filled;
    orders.push_back(order);
  }

  std::uint64_t
  Collector::clearLevel(std::shared_ptr<PriceLevel> price_level) {
    price_levels.push_back(price_level);
    return price_levels.size();
  }

  void
  Collector::commit() {
    // flush the event queue
    while (events.size()) {
      std::shared_ptr<Event> ev = events.front();
      events.pop_front();
      if (callback)
        callback(ev);
    }

    for (std::shared_ptr<PriceLevel> pl : price_levels)
      pl->commit();

    // reset order volume/filled
    for (std::shared_ptr<Order> order : orders)
      order->rebase();

    // reset order volume/filled
    if (taker_order)
      taker_order->rebase();

    reset();
  }

  void
  Collector::revert() {
    for (std::shared_ptr<PriceLevel> pl : price_levels)
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

  std::shared_ptr<Order>
  Collector::getTakerOrder() const {
    return taker_order;
  }

  std::deque<std::shared_ptr<Order>>
  Collector::getOrders() const {
    return orders;
  }

  std::deque<std::shared_ptr<Event>>
  Collector::getEvents() const {
    return events;
  }

  std::deque<std::shared_ptr<PriceLevel>>
  Collector::getPriceLevels() const {
    return price_levels;
  }

  std::uint64_t
  Collector::getClearedLevels() const {
    return price_levels.size();
  }

}  // namespace core
}  // namespace aat
