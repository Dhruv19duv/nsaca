//! Bloom Filter implementation.
//!
//! Space-efficient probabilistic data structure for set membership testing.
//! Guarantees no false negatives, with tunable false positive rate.

use std::hash::{BuildHasher, Hash, Hasher};

/// A bloom filter with configurable size and hash count.
pub struct BloomFilter {
    bits: Vec<u64>,
    num_bits: usize,
    num_hashes: usize,
    count: usize,
}

impl BloomFilter {
    /// Create a bloom filter expected to hold `expected_items` with `fp_rate` false positive probability.
    pub fn new(expected_items: usize, fp_rate: f64) -> Self {
        let ln2 = 2.0_f64.ln();
        let num_bits =
            ((-(expected_items as f64) * fp_rate.ln()) / (ln2 * ln2)).ceil() as usize;
        let num_bits = num_bits.max(64); // minimum 64 bits
        let num_hashes = ((num_bits as f64 / expected_items as f64) * ln2).ceil() as usize;
        let num_hashes = num_hashes.max(1);

        BloomFilter {
            bits: vec![0; (num_bits + 63) / 64],
            num_bits,
            num_hashes,
            count: 0,
        }
    }

    /// Create a bloom filter with explicit bit size and hash count.
    pub fn with_params(num_bits: usize, num_hashes: usize) -> Self {
        BloomFilter {
            bits: vec![0; (num_bits + 63) / 64],
            num_bits: num_bits.max(64),
            num_hashes: num_hashes.max(1),
            count: 0,
        }
    }

    /// Insert an item into the bloom filter.
    pub fn insert<T: Hash>(&mut self, item: &T) {
        let positions = self.get_positions(item);
        for pos in positions {
            let word_idx = pos / 64;
            let bit_idx = pos % 64;
            self.bits[word_idx] |= 1 << bit_idx;
        }
        self.count += 1;
    }

    /// Check if an item *might* be in the set (no false negatives).
    pub fn might_contain<T: Hash>(&self, item: &T) -> bool {
        let positions = self.get_positions(item);
        positions.iter().all(|&pos| {
            let word_idx = pos / 64;
            let bit_idx = pos % 64;
            (self.bits[word_idx] >> bit_idx) & 1 == 1
        })
    }

    /// Approximate number of items inserted.
    pub fn count(&self) -> usize {
        self.count
    }

    /// Estimated false positive rate based on current fill.
    pub fn false_positive_rate(&self) -> f64 {
        if self.count == 0 {
            return 0.0;
        }
        let ratio = (self.count as f64 * self.num_hashes as f64) / self.num_bits as f64;
        (-ratio).exp()
    }

    fn get_positions<T: Hash>(&self, item: &T) -> Vec<usize> {
        let mut hasher1 = std::collections::hash_map::RandomState::new().build_hasher();
        let mut hasher2 = std::collections::hash_map::RandomState::new().build_hasher();
        item.hash(&mut hasher1);
        item.hash(&mut hasher2);
        let h1 = hasher1.finish() as usize;
        let h2 = hasher2.finish() as usize;

        (0..self.num_hashes)
            .map(|i| (h1.wrapping_add(i.wrapping_mul(h2))) % self.num_bits)
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bloom_filter_basic() {
        let mut bf = BloomFilter::new(1000, 0.01);
        bf.insert(&"hello");
        bf.insert(&"world");

        assert!(bf.might_contain(&"hello"));
        assert!(bf.might_contain(&"world"));
        assert!(!bf.might_contain(&"goodbye")); // probably not
        assert_eq!(bf.count(), 2);
    }

    #[test]
    fn test_bloom_filter_false_positive_rate() {
        let mut bf = BloomFilter::new(100, 0.01);
        for i in 0..100 {
            bf.insert(&i);
        }
        // Should be low but not zero
        assert!(bf.false_positive_rate() < 0.1);
    }
}
