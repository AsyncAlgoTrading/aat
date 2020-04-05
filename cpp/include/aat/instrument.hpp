#pragma once

#include <string.h>
#include <aat/enums.hpp>

using namespace aat::config;

namespace aat {
namespace core {

    class Instrument {
    public:
        Instrument(const std::string& name, InstrumentType& type)
            : name(name)
            , type(type) {}

        bool operator==(const Instrument& other);
        std::string toString() const;
    
    private:
        std::string name;
        InstrumentType type;
    };

} // namespace core
} // namespace aat
