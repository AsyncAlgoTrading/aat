use super::{BaseData, EventTarget, HasBaseData};

use crate::common::{Id, Optional};
use crate::core::{ExchangeType, Instrument};

use chrono::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Data {
    base: BaseData,
    pub data: Optional<Value>,
}

impl HasBaseData for Data {
    fn get_base(&self) -> &BaseData {
        &self.base
    }
}

impl PartialEq for Data {
    fn eq(&self, other: &Self) -> bool {
        self.get_id() == other.get_id()
    }
}

impl Eq for Data {}

impl Data {
    // TODO expose all base
    pub fn new(
        id: Id,
        timestamp: Optional<DateTime<Utc>>,
        instrument: Optional<Instrument>,
        exchange: Optional<ExchangeType>,
        data: Optional<Value>,
    ) -> Data {
        Data {
            base: BaseData::new(id, timestamp, instrument, exchange),
            data,
        }
    }
}

/**********************************/
#[cfg(test)]
use serde_json::json;

#[cfg(test)]
mod data_tests {
    use super::*;

    #[test]
    fn test_eq() {
        let d1 = Data::new(1, None, None, None, Some(json!(null)));
        let d2 = Data::new(1, None, None, None, Some(json!(null)));
        let d3 = Data::new(2, None, None, None, Some(json!(null)));
        assert_eq!(d1, d2);
        assert_ne!(d1, d3);
        assert_ne!(d2, d3);
    }
}
