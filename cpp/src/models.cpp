#include <sstream>
#include <aat/enums.hpp>
#include <aat/models.hpp>

namespace aat {
namespace core {

    bool
    Data::operator==(const Data& other) {
        return (price == other.price && instrument == other.instrument && side == other.side);
    }

    bool
    Data::operator<(const Data& other) {
        return price < other.price;
    }

    std::string
    Data::toString() const {
        std::stringstream ss;
        ss << "<" << instrument.toString() << "-" << volume << "@" << price << "-" << DataType_to_string(type) << "-" << exchange << "-" << Side_to_string(side) << ">";
        return ss.str();
    }

    json
    Data::toJson() const {
        json ret;
        ret["id"] = id;
        ret["timestamp"] = timestamp;
        ret["volume"] = volume;
        ret["price"] = price;
        ret["side"] = Side_to_string(side);
        ret["type"] = DataType_to_string(type);
        ret["instrument"] = instrument.toString();
        ret["exchange"] = exchange;
        return ret;
    }

    json
    Data::perspectiveSchema() const {
        json ret;
        ret["id"] = "int";
        ret["timestamp"] = "int";
        ret["volume"] = "float";
        ret["price"] = "float";
        ret["side"] = "str";
        ret["type"] = "str";
        ret["instrument"] = "str";
        ret["exchange"] = "str";
        return ret;
    }


    std::string
    Event::toString() const {
        std::stringstream ss;
        ss << "<" << EventType_to_string(type) << "-" << target.toString() << ">";
        return ss.str();
    }

} // namespace core
} // namespace aat