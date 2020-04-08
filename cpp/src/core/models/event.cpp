#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/models/event.hpp>

namespace aat {
namespace core {
  std::string
  Event::toString() const {
    std::stringstream ss;
    ss << "<" << EventType_to_string(type) << "-" << target.toString() << ">";
    return ss.str();
  }

  json
  Event::toJson() const {
    json ret;
    ret["type"] = EventType_to_string(type);
    ret["target"] = target.toString();
    return ret;
  }

} // namespace core
} // namespace aat
