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

        // def __eq__(self, other) -> bool:
        //     return (self.price == other.price) and \
    //            (self.instrument == other.instrument) and \
    //            (self.side == other.side)

        // def __str__(self):
        //     return f'<{self.instrument}-{self.volume}@{self.price}-{self.type}-{self.exchange}-{self.side}>'

        // def __lt__(self, other) -> bool:
        //     return self.price < other.price

        // def to_json(self) -> Mapping[str, Union[str, int, float]]:
        //     return \
    //         {'id': self.id,
        //          'timestamp': self.timestamp,
        //          'volume': self.volume,
        //          'price': self.price,
        //          'side': self.side.value,
        //          'type': self.type.value,
        //          'instrument': str(self.instrument),
        //          'exchange': self.exchange}

        // @staticmethod
        // def perspectiveSchema() -> Mapping[str, Type]:
        //     return {
        //         "id": int,
        //         "timestamp": int,
        //         "volume": float,
        //         "price": float,
        //         "side": str,
        //         "type": str,
        //         "instrument": str,
        //         "exchange": str,
        //     }

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

    class Event {};

    class Order {};

    class Trade {};

} // namespace core
} // namespace aat
