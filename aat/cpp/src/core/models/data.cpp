#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/models/data.hpp>

namespace aat {
namespace core {
  bool
  Data::operator==(const Data& other) {
    return id == other.id;
  }

  str_t
  Data::toString() const {
    sstream_t ss;
    ss << "Data( id=" << id << ", timestamp=" << format_timestamp(timestamp) <<
    ", instrument=" << instrument.toString() << ", exchange=" << exchange.toString()
    << ")";
    return ss.str();
  }

  json
  Data::toJson() const {
    json ret;
    ret["id"] = id;
    ret["timestamp"] = format_timestamp(timestamp);
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
    ret["type"] = "str";
    ret["instrument"] = "str";
    ret["exchange"] = "str";
    return ret;
  }

}  // namespace core
}  // namespace aat
