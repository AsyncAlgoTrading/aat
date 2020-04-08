#include <sstream>
#include <aat/config/enums.hpp>
#include <aat/core/exchange.hpp>

namespace aat {
namespace core {
  std::string
  Exchange::toString() const {
    return name;
  }

} // namespace core
} // namespace aat
