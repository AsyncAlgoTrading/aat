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

    private:
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
        : type(type),
          target(target) {}

        std::string toString() const;

    private:
        EventType type;
        Data target;
    };


    class Order : Data {
    public:
        Order();

    private:
        DataType type; // = DataType.ORDER;
        OrderType order_type; // = OrderType.LIMIT;
        OrderFlag flag; // = OrderFlag.NONE;
        double filled = 0.0;
        Order& stop_target;
        double notional = 0.0;
    };

// class Order(Data):
//     @validator("type")
//     def _assert_type_is_order(cls, v):
//         assert v == DataType.ORDER
//         return v

//     @validator("stop_target")
//     def _assert_stop_target_not_stop(cls, v, values, **kwargs):
//         assert isinstance(v, Order)
//         assert v.order_type not in (OrderType.STOP_LIMIT, OrderType.STOP_MARKET)
//         if values['order_type'] == OrderType.STOP_LIMIT:
//             assert v.order_type == OrderType.LIMIT
//         if values['order_type'] == OrderType.STOP_MARKET:
//             assert v.order_type == OrderType.MARKET
//         return v

//     @validator("notional")
//     def _assert_notional_set_correct(cls, v, values, **kwargs) -> float:
//         if values['order_type'] == OrderType.MARKET:
//             return v
//         return values['price'] * values['volume']

//     def __str__(self):
//         return f'<{self.instrument}-{self.volume}@{self.price}-{self.exchange}-{self.side}>'

//     def to_json(self) -> Mapping[str, Union[str, int, float]]:
//         return \
//             {'id': self.id,
//              'timestamp': self.timestamp,
//              'volume': self.volume,
//              'price': self.price,
//              'side': self.side.value,
//              'instrument': str(self.instrument),
//              'exchange': self.exchange}

//     @staticmethod
//     def perspectiveSchema() -> Mapping[str, Type]:
//         return {
//             "id": int,
//             "timestamp": int,
//             "volume": float,
//             "price": float,
//             "side": str,
//             "instrument": str,
//             "exchange": str,
//         }


    class Trade {};

} // namespace core
} // namespace aat
