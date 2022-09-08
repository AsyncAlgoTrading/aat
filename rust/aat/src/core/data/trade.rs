use super::{BaseData, EventTarget, HasBaseData};

use crate::common::{Float, Id, Optional};
use crate::core::{ExchangeType, Instrument};

use chrono::prelude::*;

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Trade {
    base: BaseData,

    exchange_id: Optional<Id>,
    exchange_timestamp: Optional<DateTime<Utc>>,

    volume: Float,
    price: Float,

    maker_orders: VecDeque<Id>,
    taker_order: Id,

    // internal
    my_order: Optional<Id>,
    slippage: Optional<Float>,
    transaction_cost: Optional<Float>,
}

impl HasBaseData for Trade {
    fn get_base(&self) -> &BaseData {
        &self.base
    }
}

impl PartialEq for Trade {
    fn eq(&self, other: &Self) -> bool {
        self.get_id() == other.get_id()
    }
}

impl Trade {
    // TODO expose all base
    pub fn new(
        id: Id,
        timestamp: Optional<DateTime<Utc>>,
        instrument: Optional<Instrument>,
        exchange: Optional<ExchangeType>,
        exchange_id: Optional<Id>,
        exchange_timestamp: Optional<DateTime<Utc>>,
        volume: Float,
        price: Float,
        maker_orders: VecDeque<Id>,
        taker_order: Id,
    ) -> Trade {
        Trade {
            base: BaseData::new(id, timestamp, instrument, exchange),
            exchange_id,
            exchange_timestamp,
            volume,
            price,
            maker_orders,
            taker_order,
            my_order: None,                                 // TODO
            slippage: Some(Float::from_float(0.0)),         // TODO
            transaction_cost: Some(Float::from_float(0.0)), // TODO
        }
    }

    /* Getters */
    pub fn get_exchange_id(&self) -> Optional<Id> {
        self.exchange_id
    }

    pub fn get_exchange_timestamp(&self) -> Optional<DateTime<Utc>> {
        self.exchange_timestamp
    }

    pub fn get_volume(&self) -> Float {
        self.volume
    }

    pub fn get_price(&self) -> Float {
        self.price
    }

    /* Other */
}
