use num::cast;
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt::{Display, Formatter, Result};
use std::iter::Sum;
use std::ops::{Add, AddAssign, Sub};

#[allow(clippy::derive_hash_xor_eq)]
#[derive(Clone, Copy, Debug, Default, Hash, PartialOrd, Serialize, Deserialize)]
pub struct FloatAsLong {
    value: i64,
}

impl PartialEq for FloatAsLong {
    #[inline]
    fn eq(&self, other: &Self) -> bool {
        self.value == other.value
    }
}

impl Eq for FloatAsLong {}

impl Sum for FloatAsLong {
    #[inline]
    fn sum<I>(iter: I) -> Self
    where
        I: Iterator<Item = Self>,
    {
        iter.fold(Self { value: 0 }, |a, b| Self {
            value: a.value + b.value,
        })
    }
}

impl Sub for FloatAsLong {
    type Output = FloatAsLong;

    #[inline]
    fn sub(self, rhs: FloatAsLong) -> FloatAsLong {
        FloatAsLong {
            value: self.value - rhs.value,
        }
    }
}

#[allow(clippy::derive_ord_xor_partial_ord)]
impl Ord for FloatAsLong {
    #[inline]
    fn cmp(&self, other: &Self) -> Ordering {
        self.value.cmp(&other.value)
    }
}

impl Add for FloatAsLong {
    type Output = FloatAsLong;

    #[inline]
    fn add(self, rhs: Self) -> Self {
        Self {
            value: self.value + rhs.value,
        }
    }
}

impl AddAssign for FloatAsLong {
    #[inline]
    fn add_assign(&mut self, other: Self) {
        *self = Self {
            value: self.value + other.value,
        };
    }
}

impl Display for FloatAsLong {
    fn fmt(&self, f: &mut Formatter<'_>) -> Result {
        write!(f, "{}", self.to_float())
    }
}

impl FloatAsLong {
    pub const ZERO: FloatAsLong = FloatAsLong { value: 0 };
    pub const INFINITY: FloatAsLong = FloatAsLong { value: i64::MAX };

    pub fn to_float(&self) -> f64 {
        cast::<i64, f64>(self.value).unwrap() / cast::<i64, f64>(FLOAT_MULTIPLIER).unwrap()
    }

    pub fn from_int(val: i64) -> FloatAsLong {
        FloatAsLong {
            value: val * FLOAT_MULTIPLIER,
        }
    }

    pub fn from_float(val: f64) -> FloatAsLong {
        FloatAsLong {
            value: cast::<f64, i64>(val * cast::<i64, f64>(FLOAT_MULTIPLIER).unwrap()).unwrap(),
        }
    }
}

// NOTE: use signed for negative prices
pub type Float = FloatAsLong;

// i64 isL     -9223372036854775808 to  9223372036854775807
// so we'll do -9223372036854.775808 to 9223372036854.775807
pub const FLOAT_MULTIPLIER: i64 = 1000000;

/**********************************/
#[cfg(test)]
mod float_tests {
    use super::*;

    #[test]
    fn test_eq_from_int() {
        let f1 = Float::from_int(5);
        let f2 = Float::from_int(5);
        assert_eq!(f1, f2);
    }

    #[test]
    fn test_eq_from_float() {
        let f1 = Float::from_float(1.23456);
        let f2 = Float::from_float(1.23456);
        assert_eq!(f1, f2);
    }

    #[test]
    fn test_add() {
        let f1 = Float::from_float(1.2);
        let f2 = Float::from_float(3.4);
        let f3 = Float::from_float(4.6);
        assert_eq!(f1 + f2, f3);
    }

    #[test]
    fn test_cmp() {
        let f1 = Float::from_float(1.2);
        let f2 = Float::from_float(3.4);
        assert_eq!(f1 < f2, true);
        assert_eq!(f2 > f1, true);
    }

    #[test]
    fn test_assign() {
        let mut f1 = Float::from_float(1.2);
        let f2 = Float::from_float(4.6);
        f1 += Float::from_float(3.4);
        assert_eq!(f1, f2);
    }
}
