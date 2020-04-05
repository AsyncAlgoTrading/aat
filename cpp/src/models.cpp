#include <aat/models.hpp>

namespace aat {
namespace core {

    bool
    Data::operator==(const Data& other) {
        return (this->price == other.price && this->instrument == other.instrument && this->side == other.side);
    }

    bool
    Data::operator<(const Data& other) {}

    std::string
    Data::toString() const {}

    json
    Data::toJson() const {}

    json
    Data::perspectiveSchema() const {}

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

} // namespace core
} // namespace aat