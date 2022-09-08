use super::common::check_top_ob_book;

use crate::common::Float;
use crate::core::*;

#[cfg(test)]
mod order_book_behavior_tests {
    use super::*;

    static SEP: &'static str = "***********************************************************";
    static INST: Instrument = Instrument {};
    static EXCH: ExchangeType = ExchangeType {};

    fn build_basic_order_book(om: &OrderManager, ob: &mut LimitOrderBook) {
        // buy 10@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(10),
            Side::BUY,
            None,
        );
        ob.add(1);

        // buy 10@9
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(9),
            Side::BUY,
            None,
        );
        ob.add(2);

        // buy 10@8
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(8),
            Side::BUY,
            None,
        );
        ob.add(3);

        // sell 10@11
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(11),
            Side::SELL,
            None,
        );
        ob.add(4);

        // sell 10@12
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(12),
            Side::SELL,
            None,
        );
        ob.add(5);

        // sell 10@13
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(10),
            Float::from_int(13),
            Side::SELL,
            None,
        );
        ob.add(6);
    }

    #[test]
    fn test_simple_cross_buy() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(5),
            Float::from_int(10),
            Side::SELL,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 10.0, 5.0, 1, 11.0, 10.0, 1);

        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(5),
            Float::from_int(10),
            Side::SELL,
            None,
        );
        ob.add(8);

        println!("{SEP}\nPOST2\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 9.0, 10.0, 1, 11.0, 10.0, 1);
    }

    #[test]
    fn test_simple_cross_sell() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(5),
            Float::from_int(11),
            Side::BUY,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 10.0, 10.0, 1, 11.0, 5.0, 1);

        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(5),
            Float::from_int(11),
            Side::BUY,
            None,
        );
        ob.add(8);

        println!("{SEP}\nPOST2\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 10.0, 10.0, 1, 12.0, 10.0, 1);
    }

    #[test]
    fn test_simple_clear_buy() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(15),
            Float::from_int(10),
            Side::SELL,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 9.0, 10.0, 1, 10.0, 5.0, 1);
    }

    #[test]
    fn test_simple_clear_sell() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(15),
            Float::from_int(12),
            Side::BUY,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 10.0, 10.0, 1, 12.0, 5.0, 1);
    }

    #[test]
    fn test_simple_exhaust_buy() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(50),
            Float::from_int(5),
            Side::SELL,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 0.0, 0.0, 0, 5.0, 20.0, 1);
    }

    #[test]
    fn test_simple_exhaust_sell() {
        let om = OrderManager::new();
        let mut ob = LimitOrderBook::new(INST, EXCH, None, &om);

        build_basic_order_book(&om, &mut ob);
        println!("{SEP}\nPRE\n{ob}\n{SEP}");

        // CROSS
        // sell 5@10
        om.new_limit(
            INST,
            EXCH,
            Float::from_int(50),
            Float::from_int(15),
            Side::BUY,
            None,
        );
        ob.add(7);

        println!("{SEP}\nPOST\n{ob}\n{SEP}");

        check_top_ob_book(&ob, 0, 15.0, 20.0, 1, 0.0, 0.0, 0);
    }
}
