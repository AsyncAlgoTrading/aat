#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/models/position.hpp>

namespace aat {
namespace core {
  str_t
  Position::toString() const {
    sstream_t ss;
    ss << "<" << size << "-" << notional << ">";
    return ss.str();
  }

  json
  Position::toJson() const {
    json ret;
    ret["size"] = size;
    ret["notional"] = notional;
    ret["pnl"] = pnl;
    return ret;
  }

}  // namespace core
}  // namespace aat
