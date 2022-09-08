use super::{Manager, Tracker};
use crate::common::Id;
use crate::core::Instrument;

use std::sync::{Arc, Mutex};

#[derive(Clone, Debug)]
pub struct InstrumentManager {
    tracker: Arc<Mutex<Tracker<Instrument>>>,
}

impl InstrumentManager {
    pub fn new() -> Self {
        InstrumentManager {
            tracker: Arc::new(Mutex::new(Tracker::new())),
        }
    }

    pub fn create(&self) -> Instrument {
        let id = (*self.tracker.lock().unwrap()).next();
        let instrument = Instrument::new(id);
        *self.tracker.lock().unwrap().create(instrument)
    }
}

impl Manager for InstrumentManager {
    type Item = Instrument;

    fn get(&self, id: Id) -> Self::Item {
        *self.tracker.lock().unwrap().get(id)
    }

    fn remove(&self, id: Id) -> Self::Item {
        self.tracker.lock().unwrap().remove(id)
    }

    fn replace(&self, id: Id, item: Self::Item) {
        self.tracker.lock().unwrap().replace(id, item)
    }
}
