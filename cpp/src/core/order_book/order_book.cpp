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

  OrderBook::OrderBook(Instrument& instrument, Exchange& exchange, std::function<void(Event&)> callback)
    : instrument(instrument)
    , exchange(exchange)
    , callback(callback) {}

  void
  OrderBook::setCallback(std::function<void(Event&)> callback) {}
  void
  OrderBook::add(Order& order) {}
  void
  OrderBook::cancel(Order& order) {}
  std::vector<std::vector<float>>
  OrderBook::topOfBook() const {}
  double
  OrderBook::spread() const {}
  std::vector<std::vector<float>>
  OrderBook::level(std::uint64_t level, Side side) const {}
  std::vector<std::vector<float>>
  OrderBook::level(double price) const {}
  std::vector<std::vector<float>>
  OrderBook::levels(std::uint64_t levels) const {}

  void
  OrderBook::clearOrders(Order& order, double amount) {}

  PriceLevel*
  OrderBook::getTop(Side side, std::uint64_t cleared) {
    return nullptr;
  }

} // namespace core
} // namespace aat
