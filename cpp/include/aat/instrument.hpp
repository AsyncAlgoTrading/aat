#pragma once

#include <string.h>
#include <aat/enums.hpp>

using namespace aat::config;

namespace aat {
namespace core {

    class Instrument {
    public:
        Instrument(const py::object& name)
            : name(name.cast<std::string>())
            , type(InstrumentType::EQUITY) {}

        Instrument(const py::object& name, InstrumentType type)
            : name(name.cast<std::string>())
            , type(type) {}

        Instrument(const std::string& name, InstrumentType type)
            : name(name)
            , type(type) {}

        Instrument(const std::string& name)
            : name(name)
            , type(InstrumentType::EQUITY) {}

        bool operator==(const Instrument& other);
        std::string toString() const;

    private:
        std::string name;
        InstrumentType type;
    };

} // namespace core
} // namespace aat
