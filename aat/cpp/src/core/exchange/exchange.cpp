#include <sstream>

#include <aat/core/exchange/exchange.hpp>

namespace aat {
namespace core {
  str_t
  ExchangeType::toString() const {
    if (name != "") {
      return "Exchange+(" + name + ")";
    }
    return "No Exchange";
  }

  json
  ExchangeType::toJson() const {
    json ret;
    return ret;
  }

}  // namespace core
}  // namespace aat
