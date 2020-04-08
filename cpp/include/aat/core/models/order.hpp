#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/config/enums.hpp>
#include <aat/core/instrument.hpp>
#include <aat/core/models/data.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {
    class Order : Data {
    public:
        Order(std::uint64_t id, double timestamp, double volume, double price, Side side, Instrument instrument, Exchange exchange = Exchange(), float filled = 0.0,
            OrderType order_type = OrderType::LIMIT, OrderFlag flag = OrderFlag::NONE, Order* stop_target = nullptr, double notional = 0.0)
            : Data(id, timestamp, volume, price, side, DataType::ORDER, instrument, exchange, filled)
            , order_type(order_type)
            , flag(flag)
            , stop_target(stop_target)
            , notional(notional) {
            // enforce that stop target match stop type
            if (order_type == OrderType::STOP) {
                // FIXME
                assert(stop_target);
                assert(stop_target->order_type != OrderType::STOP);
            }

            if (order_type != OrderType::MARKET) {
                // override notional
                notional = price * volume;
            }
        }

        std::string toString() const;
        json toJson() const;
        json perspectiveSchema() const;

    protected:
        OrderType order_type = OrderType::LIMIT;
        OrderFlag flag = OrderFlag::NONE;
        Order* stop_target = nullptr;
        double notional = 0.0;
    };

} // namespace core
} // namespace aat
