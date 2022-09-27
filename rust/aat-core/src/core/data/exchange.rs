use crate::common::Id;

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct ExchangeType {}

impl Default for ExchangeType {
    fn default() -> Self {
        // TODO
        ExchangeType {}
    }
}

impl ExchangeType {
    pub fn new(_id: Id) -> ExchangeType {
        ExchangeType {}
    }
}

//     explicit ExchangeType(str_t name)
//       : name(name) {}

//     str_t toString() const;
//     virtual json toJson() const;

//     bool
//     operator==(const ExchangeType& other) const {
//       return name == other.name;
//     }
//     explicit operator bool() const { return name != ""; }
//     str_t name;
//   };

//   static ExchangeType NullExchange = ExchangeType("");

// }  // namespace core
// }  // namespace aat
