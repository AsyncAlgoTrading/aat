#include <aat/core/order_book/order_book.hpp>

namespace aat {
namespace core {
  OrderBook::OrderBook(Instrument& instrument)
    : instrument(instrument)
    , exchange(NullExchange)
    , callback(nullptr) {}

  OrderBook::OrderBook(Instrument& instrument, Exchange& exchange)
    : instrument(instrument)
    , exchange(exchange)
    , callback(nullptr) {}

  OrderBook::OrderBook(Instrument& instrument, Exchange& exchange, std::function<void(Event*)> callback)
    : instrument(instrument)
    , exchange(exchange)
    , callback(callback) {}

  void
  OrderBook::setCallback(std::function<void(Event*)> callback) {
    collector.setCallback(callback);
  }

  void
  OrderBook::add(Order* order) {}

  void
  OrderBook::cancel(Order* order) {
    double price = order->price;
    Side side = order->side;
    std::vector<double>& levels = (side == Side::BUY) ? buy_levels : sell_levels;
    std::unordered_map<double, PriceLevel*>& prices = (side == Side::BUY) ? buys : sells;

    if (std::find(levels.begin(), levels.end(), price) == levels.end()) {
      throw AATCPPException("Orderbook out of sync");
    }
    prices[price]->remove(order);

    // delete level if no more volume
    if (prices[price]->size() == 0) {
      levels.erase(std::remove(levels.begin(), levels.end(), price), levels.end());
    }
  }

  std::vector<double>
  OrderBook::topOfBook() const {
    std::vector<double> ret;
    if (buy_levels.size() > 0) {
      ret.push_back(buy_levels.back());
      ret.push_back(buys.at(buy_levels.back())->getVolume());
    } else {
      ret.push_back(0.0);
      ret.push_back(0.0);
    }

    if (sell_levels.size() > 0) {
      ret.push_back(sell_levels.front());
      ret.push_back(buys.at(sell_levels.front())->getVolume());
    } else {
      ret.push_back(std::numeric_limits<double>::infinity());
      ret.push_back(0.0);
    }
    return ret;
  }

  double
  OrderBook::spread() const {
    std::vector<double> tob = topOfBook();
    return tob[3] - tob[1];
  }

  std::vector<std::vector<double>>
  OrderBook::level(std::uint64_t level, Side side) const {}

  std::vector<std::vector<double>>
  OrderBook::level(double price) const {}

  std::vector<std::vector<double>>
  OrderBook::levels(std::uint64_t levels) const {}

  void
  OrderBook::clearOrders(Order* order, double amount) {}

  PriceLevel*
  OrderBook::getTop(Side side, std::uint64_t cleared) {
    return nullptr;
  }

} // namespace core
} // namespace aat
