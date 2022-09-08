#[allow(clippy::module_inception)]
mod order_book;

pub use order_book::*;

/******************/
#[cfg(test)]
mod tests;
