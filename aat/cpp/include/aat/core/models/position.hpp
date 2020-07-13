#pragma once

#include <deque>
#include <memory>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/models/trade.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class Position {
   public:
    Position()
      : size(0.0)
      , notional(0.0)
      , pnl(0.0)
      , unrealizedPnl(0.0) {}

    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    double size;
    double notional;
    double pnl;
    double unrealizedPnl;
    std::deque<double> pnl_history;
    std::deque<double> unrealizedPnl_history;
    std::deque<std::shared_ptr<Trade>> trades;
  };

}  // namespace core
}  // namespace aat
