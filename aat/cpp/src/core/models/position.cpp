#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/models/position.hpp>

namespace aat {
namespace core {

  Position::Position(double size, double price, timestamp_t timestamp, Instrument& instrument, ExchangeType& exchange,
    std::vector<std::shared_ptr<Trade>>& trades)
    : instrument(instrument)
    , exchange(exchange)
    , size(size)
    , price(price)
    , investment(size * price)
    , notional(size * price)
    , instrumentPrice(price)
    , pnl(0.0)
    , unrealizedPnl(0.0)
    , trades(trades) {
    size_history.push_back(size);
    size_timestamps.push_back(timestamp);

    price_history.push_back(price);
    price_timestamps.push_back(timestamp);

    investment_history.push_back(investment);
    investment_timestamps.push_back(timestamp);

    notional_history.push_back(notional);
    notional_timestamps.push_back(timestamp);

    instrumentPrice_history.push_back(price);
    instrumentPrice_timestamps.push_back(timestamp);

    pnl_history.push_back(pnl);
    pnl_timestamps.push_back(timestamp);

    unrealizedPnl_history.push_back(unrealizedPnl);
    unrealizedPnl_timestamps.push_back(timestamp);
  }

  str_t
  Position::toString() const {
    sstream_t ss;
    ss << "<" << size << "-" << notional << ">";
    return ss.str();
  }

  json
  Position::toJson() const {
    json ret;
    ret["size"] = size;
    ret["notional"] = notional;
    ret["pnl"] = pnl;
    return ret;
  }

  json
  Position::perspectiveSchema() const {
    json ret;
    ret["size"] = "float";
    ret["notional"] = "float";
    ret["pnl"] = "float";
    return ret;
  }

}  // namespace core
}  // namespace aat
