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
    OrderBook(Instrument& instrument, ExchangeType& exchange);
    OrderBook(Instrument& instrument, ExchangeType& exchange, std::function<void(Event*)> callback);

    void setCallback(std::function<void(Event*)> callback);

    void add(Order* order);
    void cancel(Order* order);

    std::vector<double> topOfBook() const;
    double spread() const;

    std::vector<double> level(std::uint64_t level) const;
    std::vector<PriceLevel*> level(double price) const;
    std::vector<std::vector<double>> levels(std::uint64_t levels) const;

    std::string toString() const;

  private:
    void clearOrders(Order* order, std::uint64_t amount);
    double getTop(Side side, std::uint64_t cleared);
    bool insort(std::vector<double> levels, double value);

    std::function<void(Event*)> callback;
    Collector collector;
    Instrument& instrument;
    ExchangeType& exchange;

    std::vector<double> buy_levels;
    std::vector<double> sell_levels;

    std::unordered_map<double, PriceLevel*> buys;
    std::unordered_map<double, PriceLevel*> sells;
  };
} // namespace core
} // namespace aat
