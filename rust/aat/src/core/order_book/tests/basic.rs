use super::common::check_top_ob_book;

use crate::common::Float;
use crate::core::*;

use rand::Rng;

#[cfg(test)]
mod order_book_simple_tests {
    use super::*;

    #[test]
    fn test_new() {
        let om = OrderManager::new();
        let ob = LimitOrderBook::new(Instrument {}, ExchangeType {}, None, &om);
        check_top_ob_book(&ob, 0, 0.0, 0.0, 0, 0.0, 0.0, 0);
    }

    #[test]
    fn test_basics() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(Instrument {}, ExchangeType {}, None, &om);

        let o1 = om.create(
            None,
            None,
            None,
            Float::from_int(10),       // volume
            Some(Float::from_int(10)), // price
            None,                      // Notional
            Side::BUY,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        let o2 = om.create(
            None,
            None,
            None,
            Float::from_int(10),       // volume
            Some(Float::from_int(20)), // price
            None,                      // Notional
            Side::SELL,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        ob.add(o1.get_id());
        ob.add(o2.get_id());

        println!("{ob}");
        check_top_ob_book(&ob, 0, 10.0, 10.0, 1, 20.0, 10.0, 1);
    }

    #[test]
    fn test_add() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(Instrument {}, ExchangeType {}, None, &om);

        let o1 = om.create(
            None,
            None,
            None,
            Float::from_int(10),       // volume
            Some(Float::from_int(10)), // price
            None,                      // Notional
            Side::BUY,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        let o2 = om.create(
            None,
            None,
            None,
            Float::from_int(10),       // volume
            Some(Float::from_int(20)), // price
            None,                      // Notional
            Side::BUY,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        let o3 = om.create(
            None,
            None,
            None,
            Float::from_int(10),       // volume
            Some(Float::from_int(20)), // price
            None,                      // Notional
            Side::BUY,
            OrderType::LIMIT,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );

        ob.add(o1.get_id());
        println!("{ob}");

        check_top_ob_book(&ob, 0, 10.0, 10.0, 1, 0.0, 0.0, 0);

        ob.add(o2.get_id());
        println!("{ob}");

        check_top_ob_book(&ob, 0, 20.0, 10.0, 1, 0.0, 0.0, 0);

        check_top_ob_book(&ob, 1, 10.0, 10.0, 1, 0.0, 0.0, 0);

        ob.add(o3.get_id());
        println!("{ob}");

        check_top_ob_book(&ob, 0, 20.0, 20.0, 2, 0.0, 0.0, 0);
    }

    #[test]
    fn test_print() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(Instrument {}, ExchangeType {}, None, &om);
        let mut rng = rand::thread_rng();

        for x in 1..20 {
            let side = if x > 10 { Side::SELL } else { Side::BUY };
            let price = Float::from_float((x as f64 / 2.0).ceil());
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
            ob.add(x);
        }
        println!("{ob}");

        let (bid, ask) = ob.get_level(0);
        assert_eq!(bid.price.to_float(), 5.0);
        assert_eq!(bid.volume.to_float() < 200.0, true);
        assert_eq!(bid.count, 2);
        assert_eq!(ask.price.to_float(), 6.0);
        assert_eq!(ask.volume.to_float() < 200.0, true);
        assert_eq!(ask.count, 2);
    }
}
