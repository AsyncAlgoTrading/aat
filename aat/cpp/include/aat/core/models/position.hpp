#pragma once

#include <deque>
#include <memory>
#include <vector>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/models/trade.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class Position {
   public:
    Position(double size, double price, timestamp_t timestamp, Instrument& instrument, ExchangeType& exchange,
      std::vector<std::shared_ptr<Trade>>& trades);

    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    const Instrument instrument;
    const ExchangeType exchange;

    double size;
    std::vector<double> size_history;
    std::vector<timestamp_t> size_timestamps;

    double price;
    std::vector<double> price_history;
    std::vector<timestamp_t> price_timestamps;

    double investment;
    std::vector<double> investment_history;
    std::vector<timestamp_t> investment_timestamps;

    double notional;
    std::vector<double> notional_history;
    std::vector<timestamp_t> notional_timestamps;

    double instrumentPrice;
    std::vector<double> instrumentPrice_history;
    std::vector<timestamp_t> instrumentPrice_timestamps;

    double pnl;
    std::vector<double> pnl_history;
    std::vector<timestamp_t> pnl_timestamps;

    double unrealizedPnl;
    std::vector<double> unrealizedPnl_history;
    std::vector<timestamp_t> unrealizedPnl_timestamps;

    std::vector<std::shared_ptr<Trade>> trades;
  };

}  // namespace core
}  // namespace aat
