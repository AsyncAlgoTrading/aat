#include <aat/core/instrument/instrument.hpp>

namespace aat {
namespace core {

  bool
  Instrument::operator==(const Instrument& other) const {
    return this->name == other.name && this->type == other.type;
  }

  str_t
  Instrument::toString() const {
    sstream_t ss;
    ss << "Instrument+(" << name << "-" << InstrumentType_to_string(type) << ")";
    return ss.str();
  }

  json
  Instrument::toJson() const {
    json ret;
    return ret;
  }

}  // namespace core
}  // namespace aat
