use crate::common::{Float, Id, Optional};

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, Default, Serialize, Deserialize)]
pub struct Account {
    id: Id,
    balance: Float,
}

impl PartialEq for Account {
    fn eq(&self, other: &Self) -> bool {
        self.get_id() == other.get_id()
    }
}

impl Eq for Account {}

impl Account {
    // TODO expose all base
    pub fn new(id: Id, balance: Optional<Float>) -> Account {
        Account {
            id,
            balance: balance.unwrap_or(Float::from_float(0.0)),
        }
    }

    pub fn get_id(&self) -> Id {
        self.id
    }

    pub fn get_balance(&self) -> Float {
        self.balance
    }

    pub fn set_balance(&mut self, balance: Float) {
        self.balance = balance;
    }
}
