#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/data/event.hpp>

namespace aat {
namespace core {
  str_t
  Event::toString() const {
    sstream_t ss;
    ss << "Event+(type=" << EventType_to_string(type) << ", target=";
    if (target) {
      ss << target->toString();
    } else {
      ss << "None";
    }
    ss << ")";
    return ss.str();
  }

  json
  Event::toJson() const {
    json ret;
    ret["type"] = EventType_to_string(type);

    if (target) {
      ret["target"] = target->toJson();
    }
    return ret;
  }

}  // namespace core
}  // namespace aat
