use crate::{LimitOrderBook, OrderBook};

pub fn check_top_ob_book(
    ob: &LimitOrderBook,
    level: usize,
    bid_price: f64,
    bid_volume: f64,
    bid_count: usize,
    ask_price: f64,
    ask_volume: f64,
    ask_count: usize,
) {
    let (bid, ask) = ob.get_level(level);
    println!("Bid: {}\nAsk: {}", bid, ask);
    assert_eq!(bid.price.to_float(), bid_price);
    assert_eq!(bid.volume.to_float(), bid_volume);
    assert_eq!(bid.count, bid_count);
    assert_eq!(ask.price.to_float(), ask_price);
    assert_eq!(ask.volume.to_float(), ask_volume);
    assert_eq!(ask.count, ask_count);
}
