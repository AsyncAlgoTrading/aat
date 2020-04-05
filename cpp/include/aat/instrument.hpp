#pragma once

#include <string.h>
#include <aat/enums.hpp>

using namespace aat::config;

namespace aat {
namespace core {

    class Instrument {
    public:
        Instrument(std::string name, InstrumentType type)
            : name(name)
            , type(type) {}

        bool operator==(const Instrument& other);

    private:
        std::string name;
        InstrumentType type;
    };

} // namespace core
} // namespace aat
