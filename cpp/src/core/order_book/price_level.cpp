#include <aat/core/order_book/price_level.hpp>

namespace aat {
namespace core {
  PriceLevel::PriceLevel(double price, Collector& collector)
    : price(price)
    , collector(collector) {}
  double
  PriceLevel::getVolume() const {
    return 0.0;
  }

  void
  PriceLevel::add(Order* order) {}
  void
  PriceLevel::remove(Order* order) {}
  Order*
  PriceLevel::cross(Order* taker_order) {
    return nullptr;
  }

  void
  PriceLevel::clear() {}
  void
  PriceLevel::commit() {}
  void
  PriceLevel::revert() {}

} // namespace core
} // namespace aat
