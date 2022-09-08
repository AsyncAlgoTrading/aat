use super::{Manager, Tracker};
use crate::common::{Float, Id, Optional};
use crate::core::{ExchangeType, Instrument, Order, OrderFlag, OrderType, Side};

use chrono::prelude::*;
use std::sync::{Arc, Mutex};

#[derive(Clone, Debug)]
pub struct OrderManager {
    tracker: Arc<Mutex<Tracker<Order>>>,
}

impl OrderManager {
    pub fn new() -> Self {
        OrderManager {
            tracker: Arc::new(Mutex::new(Tracker::new())),
        }
    }

    pub fn create(
        &self,
        timestamp: Optional<DateTime<Utc>>,
        instrument: Optional<Instrument>,
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
        let id = (*self.tracker.lock().unwrap()).next();
        let order = Order::new(
            id,
            timestamp,
            instrument,
            exchange,
            volume,
            price,
            notional,
            side,
            order_type,
            order_flag,
            participant_id,
            exchange_id,
            received_timestamp,
            update_timestamp,
            dispatch_timestamp,
            conditional_target_id,
        );
        *self.tracker.lock().unwrap().create(order)
    }

    pub fn new_limit(
        &self,
        instrument: Instrument,
        exchange: ExchangeType,
        volume: Float,
        price: Float,
        side: Side,
        order_flag: Optional<OrderFlag>,
    ) -> Order {
        let id = (*self.tracker.lock().unwrap()).next();
        let order = Order::new(
            id,
            Some(Utc::now()),
            Some(instrument),
            Some(exchange),
            volume,
            Some(price),
            None,
            side,
            OrderType::LIMIT,
            order_flag,
            None,
            None,
            None,
            None,
            None,
            None,
        );
        *self.tracker.lock().unwrap().create(order)
    }

    pub fn new_market(
        &self,
        instrument: Instrument,
        exchange: ExchangeType,
        volume: Float,
        notional: Float,
        side: Side,
    ) -> Order {
        let id = (*self.tracker.lock().unwrap()).next();
        let order = Order::new(
            id,
            Some(Utc::now()),
            Some(instrument),
            Some(exchange),
            volume,
            None,
            Some(notional),
            side,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );
        *self.tracker.lock().unwrap().create(order)
    }

    pub fn set_filled(&self, order_id: Id, to_add_to_fill: Float) {
        let order = self.get(order_id);
        let filled = order.get_filled();
        let volume = order.get_volume();

        // Clone the old order into a new order
        let mut replacement_order = order;

        // update the volume
        replacement_order.set_filled(filled + to_add_to_fill);

        // assertion
        if replacement_order.get_filled() > volume {
            panic!("Filled > volume, corruption occured!");
        }

        // replace it in the manager
        self.replace(order_id, replacement_order);
    }
}

impl Manager for OrderManager {
    type Item = Order;

    fn get(&self, id: Id) -> Self::Item {
        *self.tracker.lock().unwrap().get(id)
    }

    fn remove(&self, id: Id) -> Self::Item {
        self.tracker.lock().unwrap().remove(id)
    }

    fn replace(&self, id: Id, item: Self::Item) {
        self.tracker.lock().unwrap().replace(id, item)
    }
}
