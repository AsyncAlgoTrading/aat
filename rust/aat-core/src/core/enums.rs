use serde::{Deserialize, Serialize};

macro_rules! all_enum_derivs{
    (
        $vis:vis enum $enum_name:ident {
            $(
                $field_vis:vis $field_name:ident
            ),*$(,)+
        }
    ) => {
        #[allow(non_camel_case_types)]
        #[derive(Copy, Clone, Debug, Serialize, Deserialize, PartialEq)]
        pub enum $enum_name{
            $($field_name,)*
        }
    }
}

all_enum_derivs! {
    pub enum TradingType {
        LIVE,
        SIMULATION,
        SANDBOX,
        BACKTEST,
    }
}

all_enum_derivs! {
    pub enum Side {
        BUY,
        SELL,
    }
}

all_enum_derivs! {
    pub enum OptionType {
        CALL,
        PUT,
    }
}

all_enum_derivs! {
    pub enum EventType {
        // Heartbeat events
        HEARTBEAT,

        // Trade events
        TRADE,

        // Order events
        OPEN,
        CANCEL,
        CHANGE,
        FILL,

        // Other data events
        DATA,

        // System events
        HALT,
        CONTINUE,

        // Engine events
        ERROR,
        START,
        EXIT,

        // Order Events
        BOUGHT,
        SOLD,
        RECEIVED,
        REJECTED,
        CANCELED,
    }
}

all_enum_derivs! {
    pub enum InstrumentType {
        OTHER,
        EQUITY,
        BOND,
        OPTION,
        FUTURE,
        SPREAD,
        FUTURESOPTION,
        PERPETUALFUTURE,
        MUTUALFUND,
        COMMODITY,
        CURRENCY,
        PAIR,
        INDEX,
    }
}

impl Default for InstrumentType {
    fn default() -> Self {
        InstrumentType::EQUITY
    }
}

all_enum_derivs! {
    pub enum OrderType {
        LIMIT,
        MARKET,
        STOP,
    }
}

all_enum_derivs! {
    pub enum OrderFlag {
        NONE,
        FILL_OR_KILL,
        ALL_OR_NONE,
        IMMEDIATE_OR_CANCEL,
    }
}

impl Default for OrderFlag {
    fn default() -> Self {
        OrderFlag::NONE
    }
}

all_enum_derivs! {
    pub enum ExitRoutine {
        NONE,
        CLOSE_ALL,
    }
}
