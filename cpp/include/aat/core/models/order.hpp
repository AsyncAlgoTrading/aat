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
        Order(std::uint64_t id, double timestamp, double volume, double price,
            Side side, Instrument instrument, Exchange exchange, float filled,
            OrderType order_type, OrderFlag flag, Order* stop_target,
            double notional);

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
