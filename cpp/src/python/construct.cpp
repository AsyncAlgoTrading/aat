#include <aat/python/construct.hpp>

namespace aat {
namespace python {
  Data
  make_data(py::object id, py::object timestamp, double volume, double price, Side side, DataType type,
    Instrument instrument, ExchangeType exchange, double filled) {
    uint_t id_ = id.is_none() ? 0 : id.cast<uint_t>();
    timestamp_t timestamp_ = timestamp.is_none() ? datetime::now() : timestamp.cast<timestamp_t>();

    return Data(id_, timestamp_, volume, price, side, type, instrument, exchange, filled);
  }

}  // namespace python
}  // namespace aat
