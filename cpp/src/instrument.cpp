#include <aat/instrument.hpp>


namespace aat {
namespace core {

bool Instrument::operator==(const Instrument& other) {
    return this->name == other.name && this->type == other.type;
}

}
}

