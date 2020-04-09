#pragma once
#include <deque>
#include <vector>
#include <unordered_map>
#include <string>
#include <pybind11/pybind11.h>

#include <aat/core/order_book/price_level.hpp>
#include <aat/core/order_book/collector.hpp>
#include <aat/core/exchange.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

namespace py = pybind11;

namespace aat {
namespace core {

  class OrderBook {
  public:
    OrderBook(Instrument& instrument);
    OrderBook(Instrument& instrument, Exchange& exchange);
    OrderBook(Instrument& instrument, Exchange& exchange, std::function<void(Event*)> callback);

    void setCallback(std::function<void(Event*)> callback);

    void add(Order* order);
    void cancel(Order* order);

    std::vector<double> topOfBook() const;
    double spread() const;

    std::vector<std::vector<double>> level(std::uint64_t level = 0, Side side = Side::NONE) const;
    std::vector<std::vector<double>> level(double price = -1.0) const;
    std::vector<std::vector<double>> levels(std::uint64_t levels) const;
    /*
     * def __iter__(self);
     * def __repr__(self);
     */

  private:
    void clearOrders(Order* order, double amount);
    PriceLevel* getTop(Side side, std::uint64_t cleared);

    std::function<void(Event*)> callback;
    Collector collector;
    Instrument& instrument;
    Exchange& exchange;

    std::vector<double> buy_levels;
    std::vector<double> sell_levels;

    std::unordered_map<double, PriceLevel*> buys;
    std::unordered_map<double, PriceLevel*> sells;
  };
} // namespace core
} // namespace aat
