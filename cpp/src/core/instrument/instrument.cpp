#include <aat/core/instrument/instrument.hpp>

namespace aat {
namespace core {

  bool
  Instrument::operator==(const Instrument& other) {
    return this->name == other.name && this->type == other.type;
  }

  str_t
  Instrument::toString() const {
    sstream_t ss;
    ss << "(" << name << "-" << InstrumentType_to_string(type) << ")";
    return ss.str();
  }

}  // namespace core
}  // namespace aat
