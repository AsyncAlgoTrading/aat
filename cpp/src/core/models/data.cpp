#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/models/data.hpp>

namespace aat {
namespace core {
  bool
  Data::operator==(const Data& other) {
    return (price == other.price && instrument == other.instrument && side == other.side);
  }

  bool
  Data::operator<(const Data& other) {
    return price < other.price;
  }

  str_t
  Data::toString() const {
    std::stringstream ss;
    ss << "<" << instrument.toString() << "-" << volume << "@" << price << "-" << DataType_to_string(type) << "-"
       << exchange.toString() << "-" << Side_to_string(side) << ">";
    return ss.str();
  }

  json
  Data::toJson() const {
    json ret;
    ret["id"] = id;
    ret["timestamp"] = format_timestamp(timestamp);
    ret["volume"] = volume;
    ret["price"] = price;
    ret["side"] = Side_to_string(side);
    ret["type"] = DataType_to_string(type);
    ret["instrument"] = instrument.toString();
    ret["exchange"] = exchange.toString();
    return ret;
  }

  json
  Data::perspectiveSchema() const {
    json ret;
    ret["id"] = "int";
    ret["timestamp"] = "int";
    ret["volume"] = "float";
    ret["price"] = "float";
    ret["side"] = "str";
    ret["type"] = "str";
    ret["instrument"] = "str";
    ret["exchange"] = "str";
    return ret;
  }

}  // namespace core
}  // namespace aat
