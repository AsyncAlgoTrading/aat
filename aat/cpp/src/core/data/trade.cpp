#include <sstream>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/data/trade.hpp>

using namespace aat::common;

namespace aat {
namespace core {
  bool
  Trade::finished() const {
    return taker_order->finished();
  }

  str_t
  Trade::toString() const {
    sstream_t ss;
    ss << "Trade+( id=" << id << ", timestamp=" << format_timestamp(timestamp) << volume << "@" << price
       << ", maker_orders=" << maker_orders.size() << ", taker_order=" << taker_order->toString() << ")";
    return ss.str();
  }

  json
  Trade::toJson() const {
    json ret;
    ret["id"] = id;
    ret["timestamp"] = format_timestamp(timestamp);
    ret["volume"] = volume;
    ret["price"] = price;

    ret["taker_order"] = taker_order->toJson();

    std::vector<json> orders;
    for (auto order : maker_orders) {
      orders.push_back(order->toJson());
    }
    ret["maker_orders"] = orders;
    return ret;
  }

  json
  Trade::perspectiveSchema() const {
    json ret;
    ret["id"] = "int";
    ret["timestamp"] = "int";
    ret["volume"] = "float";
    ret["price"] = "float";

    // FIXME
    return ret;
  }

}  // namespace core
}  // namespace aat
