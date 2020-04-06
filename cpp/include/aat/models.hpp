#pragma once

#include <stdint.h>
#include <nlohmann/json.hpp>
#include <aat/enums.hpp>
#include <aat/instrument.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {

    class Data {
    public:
        Data(std::uint64_t id, std::uint64_t timestamp, double volume, double price, Side side, DataType type, Instrument instrument, std::string exchange = "", float filled = 0.0)
            : id(id)
            , timestamp(timestamp)
            , volume(volume)
            , price(price)
            , side(side)
            , type(type)
            , instrument(instrument)
            , exchange(exchange)
            , filled(filled) {}

        bool operator==(const Data& other);
        bool operator<(const Data& other);
        std::string toString() const;
        json toJson() const;
        json perspectiveSchema() const;

    protected:
        std::uint64_t id = 0;
        std::uint64_t timestamp;
        double volume;
        double price;
        Side side;
        DataType type;
        Instrument instrument;
        std::string exchange = "";
        float filled = 0.0;
    };

    class Event {
    public:
        Event(EventType type, Data target)
            : type(type)
            , target(target) {}

        std::string toString() const;
        json toJson() const;

    protected:
        EventType type;
        Data target;
    };

    class Order : Data {
    public:
        Order(std::uint64_t id, std::uint64_t timestamp, double volume, double price, Side side, Instrument instrument, std::string exchange = "", float filled = 0.0,
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

    class Trade {};

} // namespace core
} // namespace aat
