#pragma once

#include <pybind11/pybind11.h>
#include <aat/core/models/data.hpp>

namespace py = pybind11;
using namespace aat::common;
using namespace aat::config;
using namespace aat::core;

namespace aat {
namespace python {
  Data make_data(py::object id, py::object timestamp, double volume, double price, Side side, DataType type,
    Instrument instrument, ExchangeType exchange = NullExchange, double filled = 0.0);

}  // namespace python
}  // namespace aat
