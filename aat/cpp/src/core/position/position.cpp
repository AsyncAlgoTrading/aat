#include <sstream>

#include <aat/config/enums.hpp>
#include <aat/core/position/position.hpp>

namespace aat {
namespace core {

  Position::Position(double size, double price, timestamp_t timestamp, Instrument& instrument, ExchangeType& exchange,
    std::vector<std::shared_ptr<Trade>>& trades)
    : timestamp(timestamp)
    , instrument(instrument)
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
    ss << "Position+(price=" << price << ", size=" << size << ", notional=" << notional << ", pnl=" << pnl
       << ", unrealizedPnl=" << unrealizedPnl << ", instrument=" << instrument.toString()
       << ", exchange=" << exchange.toString() << ")";
    return ss.str();
  }

  json
  Position::toJson() const {
    json ret;
    ret["timestamp"] = format_timestamp(timestamp);
    ret["instrument"] = instrument.toJson();
    ret["exchange"] = exchange.toJson();

    ret["size"] = size;
    // ret["size_history"] = size_history;

    ret["notional"] = notional;
    // ret["notional_history"] = notional_history;

    ret["price"] = price;
    // ret["price_history"] = price_history;

    ret["investment"] = investment;
    // ret["investment_history"] = investment_history;

    ret["instrumentPrice"] = instrumentPrice;
    // ret["instrumentPrice_history"] = instrumentPrice_history;

    ret["pnl"] = pnl;
    // ret["pnl_history"] = pnl_history;

    ret["unrealizedPnl"] = unrealizedPnl;
    // ret["unrealizedPnl_history"] = unrealizedPnl_history;

    // ret["trades"] = trades;

    return ret;
  }

  json
  Position::perspectiveSchema() const {
    json ret;
    ret["timestamp"] = "int";
    ret["instrument"] = "str";
    ret["exchange"] = "str";
    ret["size"] = "float";
    ret["notional"] = "float";
    ret["price"] = "float";
    ret["investment"] = "float";
    ret["instrumentPrice"] = "float";
    ret["pnl"] = "float";
    ret["unrealizedPnl"] = "float";
    return ret;
  }

}  // namespace core
}  // namespace aat
