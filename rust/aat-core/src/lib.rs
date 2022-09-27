#![feature(default_free_fn)]
#![feature(map_first_last)]

pub mod common;
pub mod core;
pub use ::core::*;
pub use common::*;

// use common::*;
// use core::*;
pub fn sum_as_string(a: usize, b: usize) -> usize {
    a + b
}
