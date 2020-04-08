#pragma once
#include <deque>
#include <string>
#include <pybind11/pybind11.h>

#include <aat/core/order_book/price_level.hpp>
#include <aat/core/order_book/collector.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>

namespace py = pybind11;

namespace aat {
namespace core {

  class OrderBook {
  public:
    OrderBook(const std::string& name) {}

  private:
  };

} // namespace core
} // namespace aat
