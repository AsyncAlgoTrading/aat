#include <sstream>
#include <aat/core/exchange/exchange.hpp>

namespace aat {
namespace core {
  str_t
  ExchangeType::toString() const {
    return name;
  }

}  // namespace core
}  // namespace aat
