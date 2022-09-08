#pragma once

#include <deque>
#include <memory>
#include <vector>

#include <aat/common.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument/instrument.hpp>
#include <aat/core/exchange/exchange.hpp>
#include <aat/core/data/trade.hpp>

using namespace aat::common;
using namespace aat::config;

namespace aat {
namespace core {
  class CashPosition {
   public:
    CashPosition(double notional, timestamp_t timestamp, Instrument& instrument, ExchangeType& exchange);

    str_t toString() const;
    json toJson() const;
    json perspectiveSchema() const;

    timestamp_t timestamp;
    const Instrument instrument;
    const ExchangeType exchange;

    double notional;
    std::vector<double> notional_history;
    std::vector<timestamp_t> notional_timestamps;
  };

}  // namespace core
}  // namespace aat
