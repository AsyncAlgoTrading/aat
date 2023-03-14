#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/position/cash.hpp>

namespace aat {
namespace core {

  CashPosition::CashPosition(double notional, timestamp_t timestamp, Instrument& instrument, ExchangeType& exchange)
    : timestamp(timestamp)
    , instrument(instrument)
    , exchange(exchange)
    , notional(notional) {
    notional_history.push_back(notional);
    notional_timestamps.push_back(timestamp);
  }

  str_t
  CashPosition::toString() const {
    sstream_t ss;
    ss << "Cash+(notional=" << notional << ", instrument=" << instrument.toString()
       << ", exchange=" << exchange.toString() << ")";
    return ss.str();
  }

  json
  CashPosition::toJson() const {
    json ret;
    ret["timestamp"] = format_timestamp(timestamp);
    ret["instrument"] = instrument.toJson();
    ret["exchange"] = exchange.toJson();

    ret["notional"] = notional;
    // ret["notional_history"] = notional_history;

    return ret;
  }

  json
  CashPosition::perspectiveSchema() const {
    json ret;
    ret["timestamp"] = "int";
    ret["instrument"] = "str";
    ret["exchange"] = "str";
    ret["notional"] = "float";
    return ret;
  }

}  // namespace core
}  // namespace aat
