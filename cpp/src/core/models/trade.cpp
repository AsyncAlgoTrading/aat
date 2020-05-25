#include <sstream>
#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/models/trade.hpp>

using namespace aat::common;

namespace aat {
namespace core {
  str_t
  Trade::toString() const {
    sstream_t ss;
    ss << "<" << instrument.toString() << "-" << volume << "@" << price << "-" << exchange.toString() << ">";
    return ss.str();
  }

  json
  Trade::toJson() const {
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
  Trade::perspectiveSchema() const {
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
