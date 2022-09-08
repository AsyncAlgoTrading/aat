#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/position/account.hpp>

namespace aat {
namespace core {

  Account::Account(str_t id, ExchangeType& exchange, std::vector<std::shared_ptr<Position>>& positions)
    : id(id)
    , exchange(exchange)
    , positions(positions) {}

  void
  addPosition(std::shared_ptr<Position> position) {}

  str_t
  Account::toString() const {
    sstream_t ss;
    ss << "Account+(id=" << id << ", exchange=" << exchange.toString() << ")";
    return ss.str();
  }

  json
  Account::toJson() const {
    json ret;
    ret["id"] = id;
    ret["exchange"] = exchange.toJson();
    return ret;
  }

  json
  Account::perspectiveSchema() const {
    json ret;
    ret["id"] = "str";
    ret["exchange"] = "str";
    return ret;
  }

}  // namespace core
}  // namespace aat
