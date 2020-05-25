#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/exchange/exchange.hpp>

namespace aat {
namespace core {
  std::string
  ExchangeType::toString() const {
    return name;
  }

}  // namespace core
}  // namespace aat
