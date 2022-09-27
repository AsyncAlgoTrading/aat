use crate::common::Id;
use std::collections::HashMap;

#[derive(Clone, Debug)]
pub struct Tracker<T> {
    next_id: Id,
    map: HashMap<Id, T>,
}

impl<T> Tracker<T> {
    pub fn new() -> Self {
        Tracker {
            // NOTE: id `0` is used as invalid
            next_id: 1,
            map: HashMap::new(),
        }
    }

    pub fn next(&self) -> Id {
        self.next_id
    }

    pub fn create(&mut self, item: T) -> &mut T {
        let id = self.next_id;
        self.map.insert(id, item);
        self.next_id += 1;
        return self.map.get_mut(&id).unwrap();
    }

    pub fn get(&mut self, id: Id) -> &T {
        return self.map.get(&id).unwrap();
    }

    pub fn remove(&mut self, id: Id) -> T {
        return self.map.remove(&id).unwrap();
    }

    pub fn replace(&mut self, id: Id, item: T) {
        self.map.insert(id, item);
    }
}

pub trait Registry {
    type Item;
    fn get(&self, id: Id) -> Self::Item;
    fn remove(&self, id: Id) -> Self::Item;
    fn replace(&self, id: Id, item: Self::Item);
    // fn create(&mut self) -> &mut Self::Item;
}
