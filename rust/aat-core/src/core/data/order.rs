use super::{BaseData, EventTarget, HasBaseData};

use crate::common::{Float, Id, Optional};
use crate::core::{ExchangeType, OrderFlag, OrderType, Side};

use chrono::prelude::*;
use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct Order {
    base: BaseData,

    volume: Float,
    price: Float,
    notional: Float,

    side: Side,
    order_type: OrderType,
    order_flag: OrderFlag,

    participant_id: Optional<Id>,
    exchange_id: Optional<Id>,
    received_timestamp: Optional<DateTime<Utc>>,
    update_timestamp: Optional<DateTime<Utc>>,
    dispatch_timestamp: Optional<DateTime<Utc>>,

    conditional_target_id: Optional<Id>,

    // internal
    filled: Float,
    force_done: bool,
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct OrderArgs {
    id: Id,
    timestamp: DateTime<Utc>,
    instrument_id: Id,
    exchange: ExchangeType,

    volume: Optional<Float>,
    price: Optional<Float>,
    notional: Optional<Float>,

    side: Side,
    order_type: OrderType,
    order_flag: OrderFlag,

    participant_id: Optional<Id>,
    exchange_id: Optional<Id>,
    received_timestamp: Optional<DateTime<Utc>>,
    update_timestamp: Optional<DateTime<Utc>>,
    dispatch_timestamp: Optional<DateTime<Utc>>,

    conditional_target_id: Optional<Id>,
}

impl Default for OrderArgs {
    fn default() -> Self {
        Self {
            id: 0,
            timestamp: Utc::now(),
            instrument_id: 0,
            exchange: ExchangeType {},
            volume: None,
            price: None,
            notional: None,
            side: Side::BUY,
            order_type: OrderType::LIMIT,
            order_flag: OrderFlag::NONE,
            participant_id: None,
            exchange_id: None,
            received_timestamp: None,
            update_timestamp: None,
            dispatch_timestamp: None,
            conditional_target_id: None,
        }
    }
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct LimitOrderArgs {
    volume: Float,
    price: Float,
    side: Side,
    order_flag: OrderFlag,
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct MarketOrderArgs {
    volume: Float,
    notional: Float,
    side: Side,
}

impl HasBaseData for Order {
    fn get_base(&self) -> &BaseData {
        &self.base
    }
}

impl PartialEq for Order {
    fn eq(&self, other: &Self) -> bool {
        self.get_id() == other.get_id()
    }
}

impl Order {
    pub fn new(
        id: Id,
        timestamp: Optional<DateTime<Utc>>,
        instrument_id: Optional<Id>,
        exchange: Optional<ExchangeType>,
        volume: Float,
        price: Optional<Float>,
        notional: Optional<Float>,
        side: Side,
        order_type: OrderType,
        order_flag: Optional<OrderFlag>,
        participant_id: Optional<Id>,
        exchange_id: Optional<Id>,
        received_timestamp: Optional<DateTime<Utc>>,
        update_timestamp: Optional<DateTime<Utc>>,
        dispatch_timestamp: Optional<DateTime<Utc>>,
        conditional_target_id: Optional<Id>,
    ) -> Order {
        // Checks

        match order_type {
            OrderType::MARKET => {
                // Market order should not have price,
                match price {
                    Some(_) => {
                        panic!("No price on market orders")
                    }
                    None => {}
                }

                // Market orders can't be immediate or cancel
                match order_flag {
                    None => {}
                    Some(o) => match o {
                        OrderFlag::ALL_OR_NONE | OrderFlag::FILL_OR_KILL => {}
                        OrderFlag::IMMEDIATE_OR_CANCEL => {
                            panic!("Market orders are IOC by default")
                        }
                        _ => {}
                    },
                }
            }
            OrderType::LIMIT => {
                // limit order should have price
                match price {
                    Some(_) => {}
                    None => {
                        panic!("Must set price for market orders");
                    }
                }
            }
            _ => {}
        }

        Order {
            base: BaseData::new(id, timestamp, instrument_id, exchange),
            volume,
            price: price.unwrap_or(Float::from_float(0.0)),
            notional: notional.unwrap_or(Float::from_float(0.0)),
            side,
            order_type,
            order_flag: order_flag.unwrap_or(OrderFlag::NONE),
            participant_id,
            exchange_id,
            received_timestamp,
            update_timestamp,
            dispatch_timestamp,
            conditional_target_id,
            filled: Float::from_float(0.0),
            force_done: false,
        }
    }

    pub fn new_limit(
        id: Id,
        instrument_id: Id,
        exchange: ExchangeType,
        args: LimitOrderArgs,
    ) -> Order {
        Order::new(
            id,
            Some(Utc::now()),
            Some(instrument_id),
            Some(exchange),
            args.volume,
            Some(args.price),
            None,
            args.side,
            OrderType::LIMIT,
            Some(args.order_flag),
            None,
            None,
            None,
            None,
            None,
            None,
        )
    }

    pub fn new_market(
        id: Id,
        instrument_id: Id,
        exchange: ExchangeType,
        args: MarketOrderArgs,
    ) -> Order {
        Order::new(
            id,
            Some(Utc::now()),
            Some(instrument_id),
            Some(exchange),
            args.volume,
            None,
            Some(args.notional),
            args.side,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
    }

    /* Getters */
    pub fn get_volume(&self) -> Float {
        self.volume
    }

    pub fn set_volume(&mut self, volume: Float) {
        self.volume = volume
    }

    pub fn get_price(&self) -> Float {
        self.price
    }

    pub fn set_price(&mut self, price: Float) {
        self.price = price;
    }

    pub fn get_notional(&self) -> Float {
        self.notional
    }

    pub fn get_side(&self) -> Side {
        self.side
    }

    pub fn get_order_type(&self) -> OrderType {
        self.order_type
    }

    pub fn get_order_flag(&self) -> OrderFlag {
        self.order_flag
    }

    pub fn get_filled(&self) -> Float {
        self.filled
    }

    pub fn set_filled(&mut self, value: Float) {
        self.filled = value;
    }

    /* Other */
    pub fn get_volume_left(&self) -> Float {
        self.volume - self.filled
    }

    pub fn finished() -> bool {
        // TODO
        false
    }
    pub fn finish() {}
}

impl fmt::Display for Order {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "O({}@{})", self.get_volume_left(), self.get_price())
    }
}

/**********************************/
#[cfg(test)]
mod order_tests {
    use super::*;

    #[test]
    fn test_eq() {
        let o1 = Order::new(
            1,
            None,
            None,
            None,
            Float::from_int(10), // volume
            None,                // price
            // Some(Float::from_int(10)), // price
            None, // Notional
            Side::BUY,
            OrderType::MARKET,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        let o2 = Order::new(
            1,
            None,
            None,
            None,
            Float::from_int(20), // volume
            None,                // price
            // Some(Float::from_int(10)), // price
            None, // Notional
            Side::BUY,
            OrderType::MARKET,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        assert_eq!(o1, o2);
    }

    #[test]
    fn test_fill_volume() {
        let mut o1 = Order::new(
            1,
            None,
            None,
            None,
            Float::from_int(10), // volume
            None,                // price
            // Some(Float::from_int(10)), // price
            None, // Notional
            Side::BUY,
            OrderType::MARKET,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        o1.set_filled(Float::from_int(5));

        assert_eq!(o1.get_volume_left(), Float::from_int(5));
    }
}
