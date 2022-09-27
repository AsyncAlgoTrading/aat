use super::{Registry, Tracker};
use crate::core::{HasInstrumentBaseData, Instrument};
use crate::Id;

use std::sync::{Arc, Mutex};

#[derive(Clone, Debug)]
pub struct InstrumentRegistry<T: Instrument> {
    tracker: Arc<Mutex<Tracker<T>>>,
}

impl<T: HasInstrumentBaseData> InstrumentRegistry<T> {
    pub fn new() -> Self {
        InstrumentRegistry {
            tracker: Arc::new(Mutex::new(Tracker::new())),
        }
    }

    // TODO
    // pub fn create(&self) -> T {
    //     let id = (*self.tracker.lock().unwrap()).next();
    //     let instrument = Instrument::new(id);
    //     *self.tracker.lock().unwrap().create(instrument)
    // }
}

impl<T: HasInstrumentBaseData + Copy> Registry for InstrumentRegistry<T> {
    type Item = T;

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
