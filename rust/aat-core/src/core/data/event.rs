// NOTE: see note below
use crate::common::Id;
use crate::core::{Data, Order, Trade};
use crate::core::{EventTarget, EventType};

use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum EventData {
    Data(Data),
    Order(Order),
    Trade(Trade),
}

impl EventData {
    pub fn get_id(&self) -> Id {
        match self {
            EventData::Data(d) => d.get_id(),
            EventData::Order(o) => o.get_id(),
            EventData::Trade(t) => t.get_id(),
        }
    }
}

// #[derive(Debug, Serialize, Deserialize)]
#[derive(Clone, Debug)]
pub struct Event {
    pub event_type: EventType,
    pub target: EventData,
}

impl PartialEq for Event {
    fn eq(&self, other: &Self) -> bool {
        self.target().get_id() == other.target().get_id()
    }
}

impl Event {
    pub fn event_type(self) -> EventType {
        self.event_type
    }

    pub fn target(&self) -> &EventData {
        &self.target
    }
}
