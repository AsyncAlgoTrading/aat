#include <aat/core/order_book/order_book.hpp>

namespace aat {
namespace core {

  OrderBookIterator&
  OrderBookIterator::operator++() {
    // TODO

    return *this;
  }

  std::shared_ptr<Order> OrderBookIterator::operator*() {
    if (side == Side::SELL) {
      return (*(order_book.sells.at(price_level)))[index_in_level];
    } else {
      return (*(order_book.buys.at(price_level)))[index_in_level];
    }
  }

  bool
  OrderBookIterator::operator==(const OrderBookIterator& that) {
    // TODO
    return false;
  }

  OrderBook::OrderBook(const Instrument& instrument)
    : instrument(instrument)
    , exchange(NullExchange)
    , callback(nullptr) {}

  OrderBook::OrderBook(const Instrument& instrument, const ExchangeType& exchange)
    : instrument(instrument)
    , exchange(exchange)
    , callback(nullptr) {}

  OrderBook::OrderBook(
    const Instrument& instrument, const ExchangeType& exchange, std::function<void(std::shared_ptr<Event>)> callback)
    : instrument(instrument)
    , exchange(exchange)
    , callback(callback) {}

  void
  OrderBook::setCallback(std::function<void(std::shared_ptr<Event>)> callback) {
    collector.setCallback(callback);
  }

  void OrderBook::reset() {
    buy_levels = std::vector<double>();
    sell_levels = std::vector<double>();
    buys = std::unordered_map<double, std::shared_ptr<PriceLevel>>();
    sells = std::unordered_map<double, std::shared_ptr<PriceLevel>>();
    collector = Collector(callback);
  }

  void
  OrderBook::add(std::shared_ptr<Order> order) {
    // secondary triggered orders
    std::vector<std::shared_ptr<Order>> secondaries;

    // order is buy, so look at top of sell side
    double top = getTop(order->side, collector.getClearedLevels());

    // set levels to the right side
    std::vector<double>& levels = (order->side == Side::BUY) ? buy_levels : sell_levels;
    std::unordered_map<double, std::shared_ptr<PriceLevel>>& prices = (order->side == Side::BUY) ? buys : sells;
    std::unordered_map<double, std::shared_ptr<PriceLevel>>& prices_cross = (order->side == Side::BUY) ? sells : buys;

    // set order price appropriately
    double order_price;
    if (order->order_type == OrderType::MARKET) {
      if (order->flag == OrderFlag::NONE) {
        // price goes infinite "fill however you want"
        order_price
          = (order->side == Side::BUY) ? std::numeric_limits<double>::max() : std::numeric_limits<double>::min();
      } else {
        // with a flag, the price dictates the "max allowed price" to AON or FOK under
        order_price = order->price;
      }
    } else {
      order_price = order->price;
    }

    // check if crosses
    while (top > 0.0 && ((order->side == Side::BUY) ? order_price >= top : order_price <= top)) {
      // execute order against level
      // if returns trade, it cleared the level
      // else, order was fully executed
      std::shared_ptr<Order> trade = prices_cross[top]->cross(order, secondaries);
      if (trade) {
        // clear sell level
        top = getTop(order->side, collector.clearLevel(prices_cross[top]));
        continue;
      }
      // trade is done, check if level was cleared exactly
      if (prices_cross.at(top)->size() <= 0) {
        // level cleared exactly
        collector.clearLevel(prices_cross.at(top));
      }

      break;
    }

    // if order remaining, check rules/push to book
    if (order->filled < order->volume) {
      if (order->order_type == OrderType::MARKET) {
        // Market orders
        if (order->flag == OrderFlag::ALL_OR_NONE || order->flag == OrderFlag::FILL_OR_KILL) {
          // cancel the order, do not execute any
          collector.revert();

          // cancel the order
          collector.pushCancel(order);
          collector.commit();
        } else {
          // market order, partial
          if (order->filled > 0)
            collector.pushTrade(order, order->filled);

          // clear levels
          clearOrders(order, collector.getClearedLevels());

          // execute order
          collector.pushCancel(order);
          collector.commit();

          // execute secondaries
          for (std::shared_ptr<Order> secondary : secondaries) {
            secondary->timestamp = order->timestamp;  // adjust trigger time
            add(secondary);
          }
        }
      } else {
        // Limit Orders
        if (order->flag == OrderFlag::FILL_OR_KILL) {
          if (order->filled > 0) {
            // reverse partial
            // cancel the order, do not execute any
            collector.revert();

            // cancel the order
            collector.pushCancel(order);
            collector.commit();
          } else {
            // add to book
            collector.commit();

            // limit order, put on books
            if (insort(levels, order->price)) {
              // new price level
              prices[order->price] = std::make_shared<PriceLevel>(order->price, collector);
            }
            // add order to price level
            prices[order->price]->add(order);

            // execute secondaries
            for (std::shared_ptr<Order> secondary : secondaries) {
              secondary->timestamp = order->timestamp;  // adjust trigger time
              add(secondary);
            }
          }
        } else if (order->flag == OrderFlag::ALL_OR_NONE) {
          if (order->filled > 0) {
            // order could not fill fully, revert
            // cancel the order, do not execute any
            collector.revert();

            // cancel the order
            collector.pushCancel(order);
            collector.commit();
          } else {
            // add to book
            collector.commit();

            // limit order, put on books
            if (insort(levels, order->price)) {
              // new price level
              prices[order->price] = std::make_shared<PriceLevel>(order->price, collector);
            }
            // add order to price level
            prices[order->price]->add(order);

            // execute secondaries
            for (std::shared_ptr<Order> secondary : secondaries) {
              secondary->timestamp = order->timestamp;  // adjust trigger time
              add(secondary);
            }
          }
        } else if (order->flag == OrderFlag::IMMEDIATE_OR_CANCEL) {
          if (order->filled > 0) {
            // clear levels
            clearOrders(order, collector.getClearedLevels());

            // execute the ones that filled, kill the remainder
            collector.pushCancel(order);
            collector.commit();

            // execute secondaries
            for (std::shared_ptr<Order> secondary : secondaries) {
              secondary->timestamp = order->timestamp;  // adjust trigger time
              add(secondary);
            }

          } else {
            // add to book
            collector.commit();

            // limit order, put on books
            if (insort(levels, order->price)) {
              // new price level
              prices[order->price] = std::make_shared<PriceLevel>(order->price, collector);
            }
            // add order to price level
            prices[order->price]->add(order);

            // execute secondaries
            for (std::shared_ptr<Order> secondary : secondaries) {
              secondary->timestamp = order->timestamp;  // adjust trigger time
              add(secondary);
            }
          }
        } else {
          // clear levels
          clearOrders(order, collector.getClearedLevels());

          // execute order
          collector.commit();

          // limit order, put on books
          if (insort(levels, order->price)) {
            // new price level
            prices[order->price] = std::make_shared<PriceLevel>(order->price, collector);
          }

          // add order to price level
          prices[order->price]->add(order);

          // execute secondaries
          for (std::shared_ptr<Order> secondary : secondaries) {
            secondary->timestamp = order->timestamp;  // adjust trigger time
            add(secondary);
          }
        }
      }
    } else {
      // don't need to add trade as this is done in the price_levels

      // clear levels
      clearOrders(order, collector.getClearedLevels());

      // execute all the orders
      collector.commit();

      // execute secondaries
      for (std::shared_ptr<Order> secondary : secondaries) {
        secondary->timestamp = order->timestamp;  // adjust trigger time
        add(secondary);
      }
    }

    // clear the collector
    collector.clear();
  }

  void
  OrderBook::change(std::shared_ptr<Order> order) {
    double price = order->price;
    Side side = order->side;
    std::vector<double>& levels = (side == Side::BUY) ? buy_levels : sell_levels;
    std::unordered_map<double, std::shared_ptr<PriceLevel>>& prices = (side == Side::BUY) ? buys : sells;

    if (std::find(levels.begin(), levels.end(), price) == levels.end()) {
      throw AATCPPException("Orderbook out of sync");
    }

    // modify order in price level
    prices[price]->modify(order);
  }

  void
  OrderBook::cancel(std::shared_ptr<Order> order) {
    double price = order->price;
    Side side = order->side;
    std::vector<double>& levels = (side == Side::BUY) ? buy_levels : sell_levels;
    std::unordered_map<double, std::shared_ptr<PriceLevel>>& prices = (side == Side::BUY) ? buys : sells;

    if (std::find(levels.begin(), levels.end(), price) == levels.end()) {
      throw AATCPPException("Orderbook out of sync");
    }
    // remove order from price level
    prices[price]->remove(order);

    // delete level if no more volume
    if (prices[price]->size() == 0) {
      levels.erase(std::remove(levels.begin(), levels.end(), price), levels.end());
    }
  }

  std::shared_ptr<Order>
  OrderBook::find(std::shared_ptr<Order> order) {
    double price = order->price;
    Side side = order->side;
    std::vector<double>& levels = (side == Side::BUY) ? buy_levels : sell_levels;
    std::unordered_map<double, std::shared_ptr<PriceLevel>>& prices = (side == Side::BUY) ? buys : sells;

    if (std::find(levels.begin(), levels.end(), price) == levels.end()) {
      return nullptr;
    }

    // find in price level
    return prices[price]->find(order);
  }

  std::map<Side, std::vector<double>>
  OrderBook::topOfBookMap() const {
    std::vector<double> tob = topOfBook();
    std::map<Side, std::vector<double>> ret;
    ret[Side::BUY] = std::vector<double>();
    ret[Side::SELL] = std::vector<double>();
    ret[Side::BUY].push_back(tob[0]);
    ret[Side::BUY].push_back(tob[1]);
    ret[Side::SELL].push_back(tob[2]);
    ret[Side::SELL].push_back(tob[3]);
    return ret;
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
      ret.push_back(sells.at(sell_levels.front())->getVolume());
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

  std::vector<double>
  OrderBook::level(std::uint64_t level) const {
    std::vector<double> ret;

    // collect bids and asks at `level`
    if (buy_levels.size() > level) {
      ret.push_back(buy_levels[buy_levels.size() - level - 1]);
      ret.push_back(buys.at(buy_levels[buy_levels.size() - level - 1])->getVolume());
    } else {
      ret.push_back(0.0);
      ret.push_back(0.0);
    }

    if (sell_levels.size() > level) {
      ret.push_back(sell_levels[level]);
      ret.push_back(sells.at(sell_levels[level])->getVolume());
    } else {
      ret.push_back(std::numeric_limits<double>::infinity());
      ret.push_back(0.0);
    }
    return ret;
  }

  std::vector<std::shared_ptr<PriceLevel>>
  OrderBook::level(double price) const {
    std::vector<std::shared_ptr<PriceLevel>> ret;

    if (std::find(buy_levels.begin(), buy_levels.end(), price) == buy_levels.end()) {
      ret.push_back(buys.at(price));
    } else {
      ret.push_back(nullptr);
    }

    if (std::find(sell_levels.begin(), sell_levels.end(), price) == sell_levels.end()) {
      ret.push_back(sells.at(price));
    } else {
      ret.push_back(nullptr);
    }
    return ret;
  }

  std::map<Side, std::vector<std::vector<double>>>
  OrderBook::levelsMap(std::uint64_t levels) const {
    std::map<Side, std::vector<std::vector<double>>> ret;

    ret[Side::BUY] = std::vector<std::vector<double>>();
    ret[Side::SELL] = std::vector<std::vector<double>>();

    for (std::uint64_t i = 0; i < levels; ++i) {
      auto _level = level((std::uint64_t)i);

      // bid
      ret[Side::BUY].push_back(std::vector<double>());
      // ask
      ret[Side::SELL].push_back(std::vector<double>());

      ret[Side::BUY][i].push_back(_level[0]);
      ret[Side::BUY][i].push_back(_level[1]);
      ret[Side::SELL][i].push_back(_level[2]);
      ret[Side::SELL][i].push_back(_level[3]);
    }
    return ret;
  }

  std::vector<std::vector<double>>
  OrderBook::levels(std::uint64_t levels) const {
    std::vector<std::vector<double>> ret;
    // bid
    ret.push_back(std::vector<double>());
    // ask
    ret.push_back(std::vector<double>());

    for (std::uint64_t i = 0; i < levels; ++i) {
      auto _level = level((std::uint64_t)i);
      ret[0].push_back(_level[0]);
      ret[0].push_back(_level[1]);
      ret[1].push_back(_level[2]);
      ret[1].push_back(_level[3]);
    }
    return ret;
  }

  void
  OrderBook::clearOrders(std::shared_ptr<Order> order, std::uint64_t amount) {
    if (order->side == Side::BUY) {
      sell_levels.erase(sell_levels.begin(), sell_levels.begin() + amount);
    } else {
      buy_levels.erase(buy_levels.begin() + (buy_levels.size() - amount), buy_levels.end());
    }
  }

  double
  OrderBook::getTop(Side side, std::uint64_t cleared) {
    if (side == Side::BUY) {
      if (sell_levels.size() > cleared) {
        return sell_levels[cleared];
      } else {
        return -1;
      }
    } else {
      if (buy_levels.size() > cleared) {
        return buy_levels[buy_levels.size() - cleared - 1];
      } else {
        return -1;
      }
    }
  }

  bool
  OrderBook::insort(std::vector<double>& levels, double value) {
    auto orig_length = levels.size();
    levels.insert(std::upper_bound(levels.begin(), levels.end(), value), value);
    return orig_length != levels.size();
  }

  str_t
  OrderBook::toString() const {
    sstream_t ss;

    // show top 5 levels, then group next 5, 10, 20, etc
    // sells first
    std::vector<std::shared_ptr<PriceLevel>> sells_to_print;
    auto count = 5;
    auto orig = 5;

    for (std::uint64_t i = 0; i < sell_levels.size(); ++i) {
      if (i < 5) {
        // append to list
        sells_to_print.push_back(sells.at(sell_levels[i]));
      } else {
        // TODO implement the rest from python in C++
        break;
      }
    }

    // reverse so visually upside down
    std::reverse(sells_to_print.begin(), sells_to_print.end());

    // show top 5 levels, then group next 5, 10, 20, etc
    // buys second
    std::vector<std::shared_ptr<PriceLevel>> buys_to_print;
    count = 5;
    orig = 5;
    int i = 0;

    for (auto iter = buy_levels.end() - 1; iter > buy_levels.begin(); --iter) {
      if ((i++) < 5) {
        // append to list
        buys_to_print.push_back(buys.at(*iter));
      } else {
        // TODO implement the rest from python in C++
        break;
      }
    }
    // sell list, then line, then buy list

    // format the sells on top, tabbed to the right, with price\tvolume
    for (std::shared_ptr<PriceLevel> price_level : sells_to_print) {
      // TODO implement the rest from python in C++
      ss << "\t\t" << price_level->getPrice() << "\t\t" << price_level->getVolume() << std::endl;
    }

    ss << "-----------------------------------------------------\n";

    // format the buys on bottom, tabbed to the left, with volume\tprice so prices align
    for (std::shared_ptr<PriceLevel> price_level : buys_to_print) {
      // TODO implement the rest from python in C++
      ss << price_level->getVolume() << "\t\t" << price_level->getPrice() << std::endl;
    }
    return ss.str();
  }

  OrderBookIterator
  OrderBook::begin() const {
    return OrderBookIterator(*this);
  }

  OrderBookIterator
  OrderBook::end() const {
    return OrderBookIterator(*this, std::numeric_limits<double>::infinity(), -1, Side::BUY);
  }

}  // namespace core
}  // namespace aat
