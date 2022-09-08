#pragma once

#include <deque>
#include <memory>
#include <vector>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/position/position.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class Account {
   public:
    Account(str_t id, ExchangeType& exchange, std::vector<std::shared_ptr<Position>>& positions);

    void addPosition(std::shared_ptr<Position> position);

    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    str_t id;
    const ExchangeType exchange;
    std::vector<std::shared_ptr<Position>> positions;
  };

}  // namespace core
}  // namespace aat
