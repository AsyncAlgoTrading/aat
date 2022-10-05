use super::{
    HasInstrumentBaseData, HasInstrumentDerivativeData, HasInstrumentExtraData,
    HasInstrumentLegData, InstrumentBaseData, InstrumentDerivativeData, InstrumentExtraData,
    InstrumentLegData,
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
struct Bond {
    base: InstrumentBaseData,
    extra: InstrumentExtraData,
    legs: InstrumentLegData,
    derivative: InstrumentDerivativeData,
}

impl HasInstrumentBaseData for Bond {
    fn get_base(&self) -> &InstrumentBaseData {
        &self.base
    }
}

impl HasInstrumentExtraData for Bond {
    fn get_extra(&self) -> &InstrumentExtraData {
        &self.extra
    }
}

impl HasInstrumentLegData for Bond {
    fn get_legs(&self) -> &InstrumentLegData {
        &self.legs
    }
}

impl HasInstrumentDerivativeData for Bond {
    fn get_derivative(&self) -> &InstrumentDerivativeData {
        &self.derivative
    }
}
