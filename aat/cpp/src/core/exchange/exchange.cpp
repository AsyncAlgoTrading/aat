#include <sstream>

#include <aat/core/exchange/exchange.hpp>

namespace aat {
namespace core {
  str_t
  ExchangeType::toString() const {
    if (name != "") {
      return name;
    }
    return "No Exchange";
  }

}  // namespace core
}  // namespace aat
