#pragma once
#include <deque>
#include <vector>
#include <unordered_map>
#include <string>
#include <pybind11/pybind11.h>

#include <aat/common.hpp>
#include <aat/core/order_book/price_level.hpp>
#include <aat/core/order_book/collector.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

namespace py = pybind11;
using namespace aat::common;

namespace aat {
namespace core {

  class OrderBook {
   public:
    explicit OrderBook(const Instrument& instrument);
    OrderBook(const Instrument& instrument, const ExchangeType& exchange);
    OrderBook(const Instrument& instrument, const ExchangeType& exchange, std::function<void(Event*)> callback);

    void setCallback(std::function<void(Event*)> callback);

    void add(Order* order);
    void cancel(Order* order);

    std::vector<double> topOfBook() const;
    double spread() const;

    std::vector<double> level(uint_t level) const;
    std::vector<PriceLevel*> level(double price) const;
    std::vector<std::vector<double>> levels(uint_t levels) const;

    str_t toString() const;

   private:
    void clearOrders(Order* order, uint_t amount);
    double getTop(Side side, uint_t cleared);
    bool insort(std::vector<double>& levels, double value);  // NOLINT

    std::function<void(Event*)> callback;
    Collector collector;
    const Instrument& instrument;
    const ExchangeType& exchange;

    std::vector<double> buy_levels;
    std::vector<double> sell_levels;

    std::unordered_map<double, PriceLevel*> buys;
    std::unordered_map<double, PriceLevel*> sells;
  };
}  // namespace core
}  // namespace aat
