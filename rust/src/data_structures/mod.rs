//! High-performance data structure implementations.
//!
//! Each module provides a carefully optimized data structure suitable for
//! specific algorithmic use cases identified by the NSACA reasoning engine.

pub mod bloom_filter;
pub mod heap;
pub mod segment_tree;
pub mod suffix_array;
pub mod trie;

pub use bloom_filter::BloomFilter;
pub use heap::MinMaxHeap;
pub use segment_tree::SegmentTree;
pub use suffix_array::SuffixArray;
pub use trie::Trie;
