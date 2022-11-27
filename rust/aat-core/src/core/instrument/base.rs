use crate::common::{Id, Optional};
use crate::core::{ExchangeType, InstrumentType, OptionType, Side};

use chrono::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct InstrumentBaseData {
    id: Id,
    exchange: ExchangeType,
    instrument_type: InstrumentType,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InstrumentExtraData {
    currency: Optional<Id>,
    underlying: Optional<Id>,

    // trading_day: TradingDay,
    broker_exchange: Optional<ExchangeType>,
    broker_id: Optional<String>,

    price_increment: Optional<f32>,
    unit_value: Optional<f32>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InstrumentLegData {
    leg1: Optional<Id>,
    leg2: Optional<Id>,
    leg1_side: Optional<Side>,
    leg2_side: Optional<Side>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InstrumentDerivativeData {
    expiration: Optional<DateTime<Utc>>,
    contract_month: Optional<u8>,
    option_type: Optional<OptionType>,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct InstrumentData {
    // TODO enum out with the supported real types
    base: InstrumentBaseData,
    extra: InstrumentExtraData,
    legs: InstrumentLegData,
    derivative: InstrumentDerivativeData,
}

pub trait Instrument {
    fn get_id(&self) -> Id;
    fn get_type(&self) -> InstrumentType;
    fn get_instrument_type(&self) -> InstrumentType;
    fn get_exchange(&self) -> ExchangeType;
}

pub trait InstrumentExtra {
    fn get_currency(&self) -> Optional<Id>;
    fn get_underlying(&self) -> Optional<Id>;
    // trading_day: TradingDay,
    fn get_broker_exchange(&self) -> Optional<ExchangeType>;
    fn get_broker_id(&self) -> Optional<String>;
    fn get_price_increment(&self) -> Optional<f32>;
    fn get_unit_value(&self) -> Optional<f32>;
}

pub trait InstrumentLeg {
    fn get_leg1(&self) -> Optional<Id>;
    fn get_leg2(&self) -> Optional<Id>;
    fn get_leg1_side(&self) -> Optional<Side>;
    fn get_leg2_side(&self) -> Optional<Side>;
}

pub trait InstrumentDerivative {
    fn get_expiration(&self) -> Optional<DateTime<Utc>>;
    fn get_contract_month(&self) -> Optional<u8>;
    fn get_option_type(&self) -> Optional<OptionType>;
}

pub trait HasInstrumentBaseData {
    fn get_base(&self) -> &InstrumentBaseData;
}

pub trait HasInstrumentExtraData {
    fn get_extra(&self) -> &InstrumentExtraData;
}

pub trait HasInstrumentLegData {
    fn get_legs(&self) -> &InstrumentLegData;
}

pub trait HasInstrumentDerivativeData {
    fn get_derivative(&self) -> &InstrumentDerivativeData;
}

impl<T: HasInstrumentBaseData> Instrument for T {
    fn get_id(&self) -> Id {
        self.get_base().id
    }

    fn get_type(&self) -> InstrumentType {
        self.get_base().instrument_type
    }

    fn get_instrument_type(&self) -> InstrumentType {
        self.get_type()
    }

    fn get_exchange(&self) -> ExchangeType {
        self.get_base().exchange
    }
}

impl<T: HasInstrumentExtraData> InstrumentExtra for T {
    fn get_currency(&self) -> Optional<Id> {
        self.get_extra().currency
    }

    fn get_underlying(&self) -> Optional<Id> {
        self.get_extra().underlying
    }

    fn get_broker_exchange(&self) -> Optional<ExchangeType> {
        self.get_extra().broker_exchange
    }

    fn get_broker_id(&self) -> Optional<String> {
        self.get_extra().broker_id.clone()
        // let extra = self.get_extra();
        // match &extra.broker_id {
        //     Some(s) => Some(*s.clne),
        //     _ => None,

        // }
    }

    fn get_price_increment(&self) -> Optional<f32> {
        self.get_extra().price_increment
    }

    fn get_unit_value(&self) -> Optional<f32> {
        self.get_extra().unit_value
    }
}

impl<T: HasInstrumentLegData> InstrumentLeg for T {
    fn get_leg1(&self) -> Optional<Id> {
        self.get_legs().leg1
    }

    fn get_leg2(&self) -> Optional<Id> {
        self.get_legs().leg2
    }

    fn get_leg1_side(&self) -> Optional<Side> {
        self.get_legs().leg1_side
    }

    fn get_leg2_side(&self) -> Optional<Side> {
        self.get_legs().leg2_side
    }
}

impl<T: HasInstrumentDerivativeData> InstrumentDerivative for T {
    fn get_expiration(&self) -> Optional<DateTime<Utc>> {
        self.get_derivative().expiration
    }

    fn get_contract_month(&self) -> Optional<u8> {
        self.get_derivative().contract_month
    }

    fn get_option_type(&self) -> Optional<OptionType> {
        self.get_derivative().option_type
    }
}

impl PartialEq for InstrumentBaseData {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl Eq for InstrumentBaseData {}

impl Default for InstrumentExtraData {
    fn default() -> Self {
        Self {
            currency: None,
            underlying: None,
            broker_exchange: None,
            broker_id: None,
            price_increment: None,
            unit_value: None,
        }
    }
}

impl Default for InstrumentLegData {
    fn default() -> Self {
        Self {
            leg1: None,
            leg2: None,
            leg1_side: None,
            leg2_side: None,
        }
    }
}

impl Default for InstrumentDerivativeData {
    fn default() -> Self {
        Self {
            contract_month: None,
            expiration: None,
            option_type: None,
        }
    }
}

/**********************************/
#[cfg(test)]
use std::default::default;

#[cfg(test)]
mod base_instrument_data_tests {
    use super::*;

    #[test]
    fn test_eq() {
        let d1 = InstrumentBaseData { id: 1, ..default() };
        let d2 = InstrumentBaseData { id: 1, ..default() };
        let d3 = InstrumentBaseData { id: 2, ..default() };
        assert_eq!(d1, d2);
        assert_eq!((d1 == d3), false);
        assert_eq!((d2 == d3), false);
    }
}
