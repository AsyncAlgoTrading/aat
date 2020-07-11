#include <sstream>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/models/order.hpp>

using namespace aat::common;

namespace aat {
namespace core {
    Order::Order(uint_t id, timestamp_t timestamp,
      double volume, double price, Side side,
      Instrument instrument, ExchangeType exchange,
      double notional, OrderType order_type,
      OrderFlag flag, std::shared_ptr<Order> stop_target)
    : id(id)
    , timestamp(timestamp)
    , volume(volume)
    , price(price)
    , side(side)
    , type(DataType::ORDER)
    , instrument(instrument)
    , exchange(exchange)
    , notional(notional)
    , order_type(order_type)
    , flag(flag)
    , stop_target(stop_target)
    , filled(0.0) {
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

  str_t
  Order::toString() const {
    sstream_t ss;
    ss << "Order( instrument=" << instrument.toString() << 
    ", " << volume << "@" << price <<
    ", side=" << Side_to_string(side) <<
    ", exchange=" << exchange.toString() << ")";
    return ss.str();
  }

  json
  Order::toJson() const {
    json ret;
    ret["id"] = id;
    ret["timestamp"] = format_timestamp(timestamp);
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

}  // namespace core
}  // namespace aat
