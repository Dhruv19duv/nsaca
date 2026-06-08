//! # NSACA DSA Engine
//!
//! High-performance data structures and algorithms for the NSACA system.
//! Provides optimized implementations of complex data structures and
//! compiler-level optimizations for code generation.

pub mod algorithms;
pub mod benchmark;
pub mod data_structures;
pub mod optimizer;

/// Version of the DSA engine
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
