use crate::common::Id;

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Serialize, Deserialize)]
pub struct Instrument {}

impl Default for Instrument {
    fn default() -> Self {
        // TODO
        Instrument {}
    }
}

impl Instrument {
    pub fn new(_id: Id) -> Instrument {
        Instrument {}
    }
}
