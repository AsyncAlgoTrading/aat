#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/models/order.hpp>

namespace aat {
namespace core {
    std::string
    Order::toString() const {
        std::stringstream ss;
        ss << "<" << instrument.toString() << "-" << volume << "@" << price << "-" << exchange.toString() << "-" << Side_to_string(side) << ">";
        return ss.str();
    }

    json
    Order::toJson() const {
        json ret;
        ret["id"] = id;
        ret["timestamp"] = timestamp;
        ret["volume"] = volume;
        ret["price"] = price;
        ret["side"] = Side_to_string(side);
        ret["instrument"] = instrument.toString();
        ret["exchange"] = exchange.toString();
        return ret;
    }

    json
    Order::perspectiveSchema() const {
        json ret;
        ret["id"] = "int";
        ret["timestamp"] = "int";
        ret["volume"] = "float";
        ret["price"] = "float";
        ret["side"] = "str";
        ret["instrument"] = "str";
        ret["exchange"] = "str";
        return ret;
    }

} // namespace core
} // namespace aat
