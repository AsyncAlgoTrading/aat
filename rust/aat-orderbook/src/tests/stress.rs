use crate::{LimitOrderBook, OrderBook};

use aat_core::common::Float;
use aat_core::core::*;

use rand::Rng;
use std::time::{Duration, Instant};

#[cfg(test)]
mod order_book_simple_tests {
    use super::*;

    #[test]
    fn test_stress() {
        let count: u32 = 100_000;
        let om = OrderRegistry::new();
        let mut ob = LimitOrderBook::new(0, ExchangeType {}, None, &om);
        let mut rng = rand::thread_rng();

        let now = Instant::now();
        for x in 1..count {
            let side = if x % 2 == 0 { Side::SELL } else { Side::BUY };
            let price = Float::from_int(rng.gen_range(10..100));
            let volume = Float::from_int(rng.gen_range(10..100));

            om.create(
                None,
                None,
                None,
                volume,
                Some(price),
                None, // Notional
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
            ob.add(x.into());
        }

        let elapsed = now.elapsed();
        println!("Elapsed: {:.2?}", elapsed);
        let time = elapsed.as_secs() as f64 + elapsed.subsec_nanos() as f64 / 1_000_000_000.0;
        println!("OPS: {:.2?}", count as f64 / time);
        println!("SPO: {:.2?}", elapsed / count);
        assert!(elapsed < Duration::new(1, 300_000_000));

        // println!("{ob}");
    }
}
