#pragma once
#include <deque>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>

#include <aat/common.hpp>
#include <aat/core/order_book/price_level.hpp>
#include <aat/core/order_book/collector.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

using namespace aat::common;

namespace aat {
namespace core {
  class OrderBook;  // fwd declare

  class OrderBookIterator {
   public:
    explicit OrderBookIterator(
      const OrderBook& book, double price_level = 0.0, int index_in_level = 0, Side side = Side::SELL)
      : order_book(book)
      , price_level(price_level)
      , index_in_level(index_in_level)
      , side(side) {}

    OrderBookIterator& operator++();
    std::shared_ptr<Order> operator*();
    bool operator==(const OrderBookIterator& that);

   private:
    const OrderBook& order_book;
    double price_level;
    int index_in_level;
    Side side;
  };

  class OrderBook {
   public:
    explicit OrderBook(const Instrument& instrument);
    OrderBook(const Instrument& instrument, const ExchangeType& exchange);
    OrderBook(
      const Instrument& instrument, const ExchangeType& exchange, std::function<void(std::shared_ptr<Event>)> callback);

    void setCallback(std::function<void(std::shared_ptr<Event>)> callback);

    void add(std::shared_ptr<Order> order);
    void cancel(std::shared_ptr<Order> order);

    std::map<Side, std::vector<double>> topOfBookMap() const;  // For Binding
    std::vector<double> topOfBook() const;

    double spread() const;

    std::vector<double> level(uint_t level) const;
    std::vector<std::shared_ptr<PriceLevel>> level(double price) const;

    std::map<Side, std::vector<std::vector<double>>> levelsMap(uint_t levels) const;  // For Binding
    std::vector<std::vector<double>> levels(uint_t levels) const;

    str_t toString() const;

    // iterator
    friend class OrderBookIterator;
    typedef OrderBookIterator iterator;
    iterator begin() const;
    iterator end() const;

   private:
    void clearOrders(std::shared_ptr<Order> order, uint_t amount);
    double getTop(Side side, uint_t cleared);
    bool insort(std::vector<double>& levels, double value);  // NOLINT

    std::function<void(std::shared_ptr<Event>)> callback;
    Collector collector;
    const Instrument& instrument;
    const ExchangeType& exchange;

    std::vector<double> buy_levels;
    std::vector<double> sell_levels;

    std::unordered_map<double, std::shared_ptr<PriceLevel>> buys;
    std::unordered_map<double, std::shared_ptr<PriceLevel>> sells;
  };
}  // namespace core
}  // namespace aat
