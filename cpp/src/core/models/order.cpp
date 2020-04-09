#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/models/order.hpp>

namespace aat {
namespace core {

  Order::Order(std::uint64_t id, double timestamp, double volume, double price, Side side, Instrument instrument,
    ExchangeType exchange, double filled, OrderType order_type, OrderFlag flag, Order* stop_target, double notional)
    : Data(id, timestamp, volume, price, side, DataType::ORDER, instrument, exchange, filled)
    , order_type(order_type)
    , flag(flag)
    , stop_target(stop_target)
    , notional(notional) {
    // enforce that stop target match stop type
    if (order_type == OrderType::STOP) {
      // FIXME
      assert(stop_target);
      assert(stop_target->order_type != OrderType::STOP);
    }

    if (order_type != OrderType::MARKET) {
      // override notional
      notional = price * volume;
    }
  }

  std::string
  Order::toString() const {
    std::stringstream ss;
    ss << "<" << instrument.toString() << "-" << volume << "@" << price << "-" << exchange.toString() << "-"
       << Side_to_string(side) << ">";
    return ss.str();
  }

  json
  Order::toJson() const {
    json ret;
    ret["id"] = id;
    ret["timestamp"] = timestamp;
    ret["volume"] = volume;
    ret["price"] = price;
    ret["side"] = Side_to_string(side);
    ret["instrument"] = instrument.toString();
    ret["exchange"] = exchange.toString();
    return ret;
  }

  json
  Order::perspectiveSchema() const {
    json ret;
    ret["id"] = "int";
    ret["timestamp"] = "int";
    ret["volume"] = "float";
    ret["price"] = "float";
    ret["side"] = "str";
    ret["instrument"] = "str";
    ret["exchange"] = "str";
    return ret;
  }

} // namespace core
} // namespace aat
