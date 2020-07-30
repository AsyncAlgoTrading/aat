#include <aat/core/order_book/price_level.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  PriceLevel::PriceLevel(double price, Collector& collector)
    : price(price)
    , collector(collector)
    , orders()
    , orders_staged()
    , stop_orders()
    , stop_orders_staged() {}

  double
  PriceLevel::getVolume() const {
    double sum = 0.0;
    for (std::shared_ptr<Order> order : orders) {
      sum += (order->volume - order->filled);
    }
    return sum;
  }

  void
  PriceLevel::add(std::shared_ptr<Order> order) {
    // append order to deque
    if (order->order_type == OrderType::STOP) {
      if (orders.size() > 0 && std::find(orders.begin(), orders.end(), order->stop_target) != orders.end()) {
        return;
      }
      stop_orders.push_back(order->stop_target);
    } else {
      if (orders.size() > 0 && std::find(orders.begin(), orders.end(), order) != orders.end()) {
        collector.pushChange(order);
      } else {
        // change event
        orders.push_back(order);
        collector.pushOpen(order);
      }
    }
  }

  std::shared_ptr<Order>
  PriceLevel::find(std::shared_ptr<Order> order) {
    // check if order is in level
    if (order->price != price) {
      return nullptr;
    }

    for (auto o : orders) {
      if (o->id == order->id) {
        return o;
      }
    }

    return nullptr;
  }

  std::shared_ptr<Order>
  PriceLevel::modify(std::shared_ptr<Order> order) {
    // check if order is in level
    if (order->price != price || std::find(orders.begin(), orders.end(), order) == orders.end()) {
      // something is wrong
      throw AATCPPException("Order not found in price level!");
    }
    // remove order
    orders.erase(std::find(orders.begin(), orders.end(), order));  // FIXME c++

    // trigger cancel event
    collector.pushCancel(order);

    // return the order
    return order;
  }

  std::shared_ptr<Order>
  PriceLevel::remove(std::shared_ptr<Order> order) {
    // check if order is in level
    if (order->price != price || std::find(orders.begin(), orders.end(), order) == orders.end()) {
      // something is wrong
      throw AATCPPException("Order not found in price level!");
    }
    // remove order
    orders.erase(std::find(orders.begin(), orders.end(), order));  // FIXME c++

    // trigger cancel event
    collector.pushCancel(order);

    // return the order
    return order;
  }

  std::shared_ptr<Order>
  PriceLevel::cross(std::shared_ptr<Order> taker_order, std::vector<std::shared_ptr<Order>>& secondaries) {
    if (taker_order->order_type == OrderType::STOP) {
      add(taker_order);
      return nullptr;
    }

    if (taker_order->filled == taker_order->volume) {
      // already filled
      for (std::shared_ptr<Order> order : stop_orders)
        secondaries.push_back(order);
      return nullptr;
    } else if (taker_order->filled > taker_order->volume) {
      throw AATCPPException("Unknown error occurred - order book is corrupt");
    }

    while (taker_order->filled < taker_order->volume && orders.size() > 0) {
      // need to fill original volume - filled so far
      double to_fill = taker_order->volume - taker_order->filled;

      // pop maker order from list
      std::shared_ptr<Order> maker_order = orders.front();
      orders.pop_front();

      // add to staged in case we need to revert
      orders_staged.push_back(maker_order);

      // remaining in maker_order
      double maker_remaining = maker_order->volume - maker_order->filled;

      if (maker_remaining > to_fill) {
        // handle fill or kill/all or nothing
        if (maker_order->flag == OrderFlag::FILL_OR_KILL || maker_order->flag == OrderFlag::ALL_OR_NONE) {
          // kill the maker order and continue
          collector.pushCancel(maker_order);
          continue;
        } else {
          // maker_order is partially executed
          maker_order->filled += to_fill;

          // will exit loop
          taker_order->filled = taker_order->volume;
          collector.pushFill(taker_order);

          // change event
          collector.pushChange(maker_order, true);

          if (maker_order->flag == OrderFlag::IMMEDIATE_OR_CANCEL) {
            // cancel maker event, don't put in queue
            collector.pushCancel(maker_order);
          } else {
            // push back in deque
            orders.push_front(maker_order);
          }
        }
      } else if (maker_remaining < to_fill) {
        // partially fill it regardles
        // this will either trigger the revert in order_book,
        // or it will be partially executed
        taker_order->filled += maker_remaining;

        if (taker_order->flag == OrderFlag::ALL_OR_NONE) {
          // taker order can't be filled, push maker back and cancel taker
          // push back in deque
          orders.push_front(maker_order);

          for (std::shared_ptr<Order> order : stop_orders)
            secondaries.push_back(order);
          return nullptr;
        } else {
          // maker_order is fully executed
          // don't append to deque
          // tell maker order filled
          collector.pushChange(taker_order);
          collector.pushFill(maker_order, true);
        }
      } else {
        // exactly equal
        maker_order->filled += to_fill;
        taker_order->filled += maker_remaining;

        collector.pushFill(taker_order);
        collector.pushFill(maker_order, true);
      }
    }

    if (taker_order->filled == taker_order->volume) {
      // execute the taker order
      collector.pushTrade(taker_order);

      // return nothing to signify to stop
      for (std::shared_ptr<Order> order : stop_orders)
        secondaries.push_back(order);
      return nullptr;
    } else if (taker_order->filled > taker_order->volume) {
      throw AATCPPException("Unknown error occurred - order book is corrupt");
    }

    // return order, this level is cleared and the order still has volume
    for (std::shared_ptr<Order> order : stop_orders)
      secondaries.push_back(order);
    return taker_order;
  }

  void
  PriceLevel::clear() {
    orders.clear();
    orders_staged.clear();
    stop_orders.clear();
    stop_orders_staged.clear();
  }

  void
  PriceLevel::commit() {
    clear();
  }

  void
  PriceLevel::revert() {
    orders.clear();
    orders.insert(
      orders.begin(), std::make_move_iterator(orders_staged.begin()), std::make_move_iterator(orders_staged.end()));
    orders_staged.clear();

    stop_orders.clear();
    stop_orders.insert(stop_orders.begin(), std::make_move_iterator(stop_orders_staged.begin()),
      std::make_move_iterator(stop_orders_staged.end()));
    stop_orders_staged.clear();
  }

}  // namespace core
}  // namespace aat
