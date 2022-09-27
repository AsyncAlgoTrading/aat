use super::exchange::ExchangeType;

use crate::common::{Id, Optional};

use chrono::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
pub struct BaseData {
    id: Id,
    timestamp: DateTime<Utc>,
    instrument_id: Id,
    exchange: ExchangeType,
}

impl BaseData {
    // TODO expose all
    pub fn new(
        id: Id,
        timestamp: Optional<DateTime<Utc>>,
        instrument_id: Optional<Id>,
        exchange: Optional<ExchangeType>,
    ) -> BaseData {
        BaseData {
            id,
            timestamp: timestamp.unwrap_or(Utc::now()),
            instrument_id: instrument_id.unwrap_or(0),
            exchange: exchange.unwrap_or(ExchangeType {}),
        }
    }
}

pub trait EventTarget {
    fn get_id(&self) -> Id;
}

pub trait HasBaseData {
    fn get_base(&self) -> &BaseData;
}

pub trait BaseDataGetters {
    fn get_timestamp(&self) -> DateTime<Utc>;
    fn get_instrument_id(&self) -> Id;
    fn get_exchange(&self) -> ExchangeType;
}

impl<T: HasBaseData> EventTarget for T {
    fn get_id(&self) -> Id {
        self.get_base().id
    }
}

impl<T: HasBaseData> BaseDataGetters for T {
    fn get_timestamp(&self) -> DateTime<Utc> {
        self.get_base().timestamp
    }

    fn get_instrument_id(&self) -> Id {
        self.get_base().instrument_id
    }

    fn get_exchange(&self) -> ExchangeType {
        self.get_base().exchange
    }
}

impl PartialEq for BaseData {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for BaseData {}

/**********************************/
#[cfg(test)]
use std::default::default;

#[cfg(test)]
mod base_data_tests {
    use super::*;

    #[test]
    fn test_eq() {
        let d1 = BaseData { id: 1, ..default() };

        let d2 = BaseData { id: 1, ..default() };

        let d3 = BaseData { id: 2, ..default() };

        assert_eq!(d1, d2);
        assert_eq!((d1 == d3), false);
        assert_eq!((d2 == d3), false);
    }
}
