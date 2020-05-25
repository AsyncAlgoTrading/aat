#pragma once

#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11_json/pybind11_json.hpp>

#include <aat/config/enums.hpp>
#include <aat/core/models/data.hpp>
#include <aat/core/models/event.hpp>
#include <aat/core/models/order.hpp>
#include <aat/core/models/trade.hpp>
#include <aat/core/order_book/order_book.hpp>

namespace py = pybind11;

namespace aat {
namespace python {
  using aat::core;
  Data
  make_data()

}  // namespace python
}  // namespace aat
