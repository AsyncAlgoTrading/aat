#include <sstream>
#include <aat/instrument.hpp>

namespace aat {
namespace core {

    bool
    Instrument::operator==(const Instrument& other) {
        return this->name == other.name && this->type == other.type;
    }

    std::string Instrument::toString() const {
        std::stringstream ss;
        ss << "(" << name << "-" << InstrumentType_to_string(type) << ")";
        return ss.str();
    }

} // namespace core
} // namespace aat
