use aat_core::common::{Float, Id, Optional};
use aat_core::core::{
    BaseDataGetters, Event, EventData, EventType, ExchangeType, OrderFlag, OrderRegistry,
    OrderType, Registry, Side, Trade,
};

use chrono::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};
use std::fmt::{Display, Formatter, Result};

pub struct LimitOrderBook<'a> {
    // static data
    instrument_id: Id,
    exchange: ExchangeType,
    order_flags: HashSet<OrderFlag>,

    order_registry: &'a OrderRegistry,

    // Top to bottom
    // e.g. [5, ..., 1]
    buys: VecDeque<Float>,

    // Bottom to top
    // e.g. [6, ..., 10]
    sells: VecDeque<Float>,

    levels: HashMap<Float, VecDeque<Id>>,
}

pub struct TopOfBook {
    pub bid: PriceLevelView,
    pub ask: PriceLevelView,
}

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct PriceLevelView {
    pub price: Float,
    pub volume: Float,
    pub count: usize,
}

impl Display for PriceLevelView {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        write!(f, "({}, {}, {})", self.price, self.volume, self.count)
    }
}

impl PriceLevelView {
    pub fn new(price: Float, volume: Float, count: usize) -> Self {
        PriceLevelView {
            price,
            volume,
            count,
        }
    }
}

pub trait OrderBook<'a> {
    type Item;
    fn new(
        instrument_id: Id,
        exchange: ExchangeType,
        order_flags: Optional<HashSet<OrderFlag>>,
        order_registry: &'a OrderRegistry,
    ) -> Self::Item;

    fn get_instrument(&self) -> Id;
    fn get_instrument_id(&self) -> Id;
    fn get_exchange(&self) -> ExchangeType;
    fn get_order_flags(&self) -> HashSet<OrderFlag>;

    fn get_level(&self, level: usize) -> (PriceLevelView, PriceLevelView);

    fn add(&mut self, order_id: Id) -> VecDeque<Event>;
    // fn add_order(&mut self, order: &mut Order) -> VecDeque<Event>;

    fn modify(&mut self, order_id: Id, volume: Float) -> VecDeque<Event>;
    // fn modify_order(&mut self, order: &mut Order) -> VecDeque<Event>;

    fn replace(&mut self, existing_order_id: Id, replacement_order_id: Id) -> VecDeque<Event>;
    // fn replace_order(&mut self, existing_order: &mut Order, replacement_order_id: &mut Order) -> VecDeque<Event>;

    fn cancel(&mut self, order_id: Id) -> VecDeque<Event>;
    // fn cancel_order(&mut self, order: &mut Order) -> VecDeque<Event>;
}

impl<'a> OrderBook<'a> for LimitOrderBook<'a> {
    type Item = LimitOrderBook<'a>;

    fn new(
        instrument_id: Id,
        exchange: ExchangeType,
        order_flags: Optional<HashSet<OrderFlag>>,
        order_registry: &'a OrderRegistry,
    ) -> LimitOrderBook<'a> {
        LimitOrderBook {
            instrument_id,
            exchange,
            order_flags: order_flags.unwrap_or_default(),
            order_registry,
            buys: VecDeque::new(),
            sells: VecDeque::new(),
            levels: HashMap::new(),
        }
    }

    fn get_instrument(&self) -> Id {
        self.instrument_id
    }

    fn get_instrument_id(&self) -> Id {
        self.instrument_id
    }

    fn get_exchange(&self) -> ExchangeType {
        self.exchange
    }

    fn get_order_flags(&self) -> HashSet<OrderFlag> {
        self.order_flags.clone()
    }

    fn add(&mut self, order_id: Id) -> VecDeque<Event> {
        let mut events = VecDeque::new();
        events.extend(self.add_internal(order_id).iter().cloned());
        events
    }

    fn modify(&mut self, order_id: Id, volume: Float) -> VecDeque<Event> {
        // Note: you cannot modify price, only volume
        let mut events = VecDeque::new();
        let existing_order = self.order_registry.get(order_id);
        let price = existing_order.get_price();

        // TODO do here?
        // if existing_order.get_price() != replacement_order.get_price() {
        //     // nothing to do, not allowed
        //     return events;
        // }

        // Clone the old order into a new order
        let mut replacement_order = existing_order;

        // update the volume
        replacement_order.set_volume(volume);

        // replace it in the Registry
        self.order_registry.replace(order_id, replacement_order);

        // update the volume of the price level
        let price_level = self.levels.get_mut(&price).unwrap();
        price_level.push_back(order_id); // TODO opt: push a tuple with volume?

        // Create the change event
        events.push_back(Event {
            event_type: EventType::CHANGE,
            target: EventData::Order(replacement_order),
        });

        // Return the events
        events
    }

    fn replace(&mut self, existing_order_id: Id, replacement_order_id: Id) -> VecDeque<Event> {
        let mut events = VecDeque::new();

        // Cancel and replace
        events.extend(self.cancel(existing_order_id).iter().cloned());
        events.extend(self.add(replacement_order_id).iter().cloned());

        // Return the events
        events
    }

    fn cancel(&mut self, order_id: Id) -> VecDeque<Event> {
        let mut events = VecDeque::new();
        let order = self.order_registry.get(order_id);
        let price = order.get_price();

        // Remove from price level
        let price_level = self.levels.get_mut(&price).unwrap();
        price_level.retain(|&id| id != order_id);

        if price_level.is_empty() {
            // remove level from vec
            match order.get_side() {
                Side::BUY => self.buys.retain(|&f| f != price),
                Side::SELL => self.sells.retain(|&f| f != price),
            }
        }

        // Construct event
        events.push_back(Event {
            event_type: EventType::CANCEL,
            target: EventData::Order(order),
        });

        // And return teh events
        events
    }

    fn get_level(&self, level: usize) -> (PriceLevelView, PriceLevelView) {
        let buy_price = self.buys.get(level);
        let sell_price = self.sells.get(level);

        (
            match buy_price {
                None => PriceLevelView::new(Float::ZERO, Float::ZERO, 0),
                Some(&bp) => {
                    PriceLevelView::new(bp, self.volume_at_level(bp), self.count_at_level(bp))
                }
            },
            match sell_price {
                None => PriceLevelView::new(Float::ZERO, Float::ZERO, 0),
                Some(&sp) => {
                    PriceLevelView::new(sp, self.volume_at_level(sp), self.count_at_level(sp))
                }
            },
        )
    }
}

impl LimitOrderBook<'_> {
    fn volume_at_level(&self, level: Float) -> Float {
        self.levels
            .get(&level)
            .unwrap()
            .iter()
            .map(|&order_id| self.order_registry.get(order_id).get_volume_left())
            .sum()
    }

    fn count_at_level(&self, level: Float) -> usize {
        self.levels[&level].len()
    }

    fn add_internal(&mut self, taker_order_id: Id) -> VecDeque<Event> {
        let mut events: VecDeque<Event> = VecDeque::new();

        // For any cross, some orders will be:
        //   - filled completely
        //      - resting orders
        //      - taker order itself
        //   - partially filled
        //      - last resting order touched by taker order
        //      - taker order itself after exhausting available liquidity
        //   - cancelled
        //      - resting order (if fill-or-kill)
        //      - taker order itself (if fill-or-kill)
        //   - new
        //      - conditional orders
        let mut filled: VecDeque<(Id, Float)> = VecDeque::new();
        let mut partial: VecDeque<(Id, Float, Float)> = VecDeque::new();
        // let mut new: VecDeque<Id> = VecDeque::new();

        // TODO only used when flags and conditional orders are enabled
        // let mut _cancelled: VecDeque<Id> = VecDeque::new();

        let order = self.order_registry.get(taker_order_id);
        let price: Float = order.get_price();
        let side: Side = order.get_side();

        let order_type: OrderType = order.get_order_type();
        let order_flag: OrderFlag = order.get_order_flag();

        let mut filled_so_far_in_txn = Float::from_int(0);
        let volume_left_to_fill = order.get_volume_left();

        // whether or not to apply the changes
        // of the given order, or reverse them
        let mut undo = false;

        loop {
            if filled_so_far_in_txn == volume_left_to_fill {
                // done filling, taker was filled completely
                break;
            }

            let top_of_buys = *self.buys.get(0).unwrap_or(&Float::ZERO);
            let bottom_of_sells = *self.sells.get(0).unwrap_or(&Float::INFINITY);

            let side_of_book_to_cross: &mut VecDeque<Float> = match side {
                Side::BUY => &mut self.sells,
                Side::SELL => &mut self.buys,
            };

            let crossing = match side {
                Side::BUY => price >= bottom_of_sells && side_of_book_to_cross.len() > 0,
                Side::SELL => price <= top_of_buys && side_of_book_to_cross.len() > 0,
            };

            if crossing {
                // cross
                let price_level_price = side_of_book_to_cross[0];
                let orders_at_price_level = self.levels.get_mut(&price_level_price).unwrap();

                // Grab the first order in line
                let maker_order_id = orders_at_price_level.pop_front().unwrap();
                let maker_order = self.order_registry.get(maker_order_id);
                let maker_order_volume = maker_order.get_volume_left();

                let available_liquidity = maker_order_volume;
                let remaining_to_fill = volume_left_to_fill - filled_so_far_in_txn;

                assert!(remaining_to_fill >= Float::from_int(0));

                match maker_order.get_order_flag() {
                    OrderFlag::NONE => {
                        if available_liquidity > remaining_to_fill {
                            // add the modify to the partial vec
                            partial.push_back((
                                maker_order_id,
                                maker_order_volume - remaining_to_fill,
                                price_level_price,
                            ));

                            // add volume to running
                            filled_so_far_in_txn += remaining_to_fill;
                        } else {
                            // modify the maker order
                            filled.push_back((maker_order_id, available_liquidity));

                            // add volume to running
                            filled_so_far_in_txn += available_liquidity;
                        }
                    }
                    _ => {
                        // TODO cancel and move on if FOK
                        panic!("Not implemented yet");
                    }
                }

                // remove price level if empty now
                if orders_at_price_level.is_empty() {
                    // clear level
                    side_of_book_to_cross.pop_front();
                    continue;
                }
            } else {
                // stop looping
                break;
            }
        }

        // after any crossing, handle the after effects
        if filled_so_far_in_txn < volume_left_to_fill {
            // TODO if fill or kill, cancel whole txn
            match order_type {
                OrderType::LIMIT => {
                    match order_flag {
                        OrderFlag::NONE => {
                            // update order filled amount
                            self.order_registry
                                .set_filled(taker_order_id, filled_so_far_in_txn);

                            // emplace
                            match side {
                                Side::BUY => {
                                    match self.buys.binary_search_by(|e| e.cmp(&price).reverse()) {
                                        Ok(_pos) => {
                                            self.levels
                                                .get_mut(&price)
                                                .unwrap()
                                                .push_back(taker_order_id);
                                        }
                                        Err(pos) => {
                                            self.buys.insert(pos, price);
                                            self.levels.insert(price, VecDeque::new());
                                            self.levels
                                                .get_mut(&price)
                                                .unwrap()
                                                .push_back(taker_order_id);
                                        }
                                    }
                                }
                                Side::SELL => match self.sells.binary_search(&price) {
                                    Ok(_pos) => {
                                        self.levels
                                            .get_mut(&price)
                                            .unwrap()
                                            .push_back(taker_order_id);
                                    }
                                    Err(pos) => {
                                        self.sells.insert(pos, price);
                                        self.levels.insert(price, VecDeque::new());
                                        self.levels
                                            .get_mut(&price)
                                            .unwrap()
                                            .push_back(taker_order_id);
                                    }
                                },
                            }
                        }
                        _ => {
                            panic!("Not implemented");
                        }
                    }
                }
                OrderType::MARKET => match order_flag {
                    OrderFlag::IMMEDIATE_OR_CANCEL => {
                        // flag not supported
                        panic!("Not implemented;");
                    }
                    OrderFlag::ALL_OR_NONE | OrderFlag::FILL_OR_KILL => {
                        // undo the action
                        undo = true;
                    }
                    _ => {
                        // nothing else to do
                    }
                },
                _ => {
                    panic!("Not implemented");
                }
            }
        }

        // sanity check
        if partial.len() > 1 {
            println!("{partial:?}");
            panic!("Partial should only be length 1");
        }

        if undo {
            panic!("not implemented yet");
        } else {
            if filled_so_far_in_txn > Float::from_int(0) {
                let mut maker_orders: VecDeque<Id> = VecDeque::new();
                // Handle the fills
                filled.iter().for_each(|&(order_id, to_add_to_fill)| {
                    maker_orders.push_back(order_id);
                    self.order_registry.set_filled(order_id, to_add_to_fill)
                });
                partial
                    .iter()
                    .for_each(|&(order_id, to_add_to_fill, price_level_price)| {
                        maker_orders.push_back(order_id);

                        self.order_registry.set_filled(order_id, to_add_to_fill);

                        // readd to level
                        let orders_at_price_level =
                            self.levels.get_mut(&price_level_price).unwrap();
                        orders_at_price_level.push_front(order_id);

                        let side_of_book_to_cross: &mut VecDeque<Float> = match side {
                            Side::BUY => &mut self.sells,
                            Side::SELL => &mut self.buys,
                        };

                        if orders_at_price_level.len() == 1 {
                            side_of_book_to_cross.push_front(price_level_price);
                        }
                    });

                let trade = Trade::new(
                    0, // TODO
                    Some(Utc::now()),
                    Some(order.get_instrument_id()),
                    Some(order.get_exchange()),
                    None,
                    None,
                    filled_so_far_in_txn,
                    Float::from_float(0.0), // TODO calc avg price
                    maker_orders,
                    taker_order_id,
                );

                // trade events
                events.push_back(Event {
                    event_type: EventType::TRADE,
                    target: EventData::Trade(trade),
                });
            }

            // TODO
            // new.iter()
            //     .for_each(|&order_id| events.extend(self.add_internal(order_id)));
        }

        // return the events generated
        events
    }
}

impl Display for LimitOrderBook<'_> {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        let mut ret = "".to_string();
        ret += "OrderBook {\n";

        self.sells.iter().rev().for_each(|level| {
            let price = level.to_float().to_string();
            let volume = self.volume_at_level(*level).to_float();
            let volume_str = volume.to_string();
            let count = self.count_at_level(*level);

            if volume > 0.0 {
                ret += "\t\t";
                ret += &price;
                ret += "\t";
                ret += &volume_str;
                ret += "\t";
                ret += &count.to_string();
                ret += "\n";
            }
        });
        ret += "====================================\n";
        self.buys.iter().for_each(|level| {
            let price = level.to_float().to_string();
            let volume = self.volume_at_level(*level).to_float();
            let volume_str = volume.to_string();
            let count = self.count_at_level(*level);
            if volume > 0.0 {
                ret += "\t";
                ret += &volume_str;
                ret += "\t";
                ret += &price;
                ret += "\t\t";
                ret += &count.to_string();
                ret += "\n";
            }
        });
        ret += "}";
        write!(f, "{}", ret)
    }
}
