#pragma once

#include <stdint.h>
#include <deque>
#include <nlohmann/json.hpp>
#include <aat/enums.hpp>
#include <aat/instrument.hpp>

// for convenience
using json = nlohmann::json;
using namespace aat::config;

namespace aat {
namespace core {

    class Exchange {
    public:
        Exchange(std::string name = "") 
        : name(name) {}

        std::string toString() const;

    private:
        std::string name;
    };

    class Data {
    public:
        Data(std::uint64_t id, double timestamp, double volume, double price, Side side, DataType type, Instrument instrument, Exchange exchange = Exchange(), float filled = 0.0)
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
        std::uint64_t id;
        double timestamp;
        double volume;
        double price;
        Side side;
        DataType type;
        Instrument instrument;
        Exchange exchange;
        float filled;
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

    class Trade : Data {
    public:
        Trade(std::uint64_t id, double timestamp, double volume, double price, Side side, Instrument instrument, Exchange exchange = Exchange(), float filled = 0.0,
              std::deque<Order*> maker_orders = std::deque<Order*>(), Order* taker_order = nullptr)
            : Data(id, timestamp, volume, price, side, DataType::TRADE, instrument, exchange, filled)
            , maker_orders(maker_orders)
            , taker_order(taker_order)
            , _slippage(0.0)
            , _transaction_cost(0.0) {
            // enforce that stop target match stop type
            assert(maker_orders.length > 0);
        }

        double slippage() const { return 0.0; }
        double transactionCost() const { return 0.0; }
        std::string toString() const;
        json toJson() const;
        json perspectiveSchema() const;

    protected:
        std::deque<Order*> maker_orders;
        Order* taker_order;
        double _slippage;
        double _transaction_cost;
    };


} // namespace core
} // namespace aat
