//! Benchmarking engine for algorithmic performance analysis.

use std::time::{Duration, Instant};

/// A single benchmark result.
#[derive(Debug, Clone)]
pub struct BenchmarkResult {
    pub name: String,
    pub iterations: usize,
    pub total_time: Duration,
    pub avg_time: Duration,
    pub ops_per_sec: f64,
}

/// Benchmark runner that measures execution time of closures.
pub struct BenchmarkRunner;

impl BenchmarkRunner {
    /// Benchmark a closure over multiple iterations.
    pub fn bench<F: FnMut()>(name: &str, iterations: usize, mut f: F) -> BenchmarkResult {
        // Warmup
        for _ in 0..iterations.min(100) {
            f();
        }

        let start = Instant::now();
        for _ in 0..iterations {
            f();
        }
        let total_time = start.elapsed();
        let avg_time = total_time / iterations as u32;
        let ops_per_sec = iterations as f64 / total_time.as_secs_f64();

        BenchmarkResult {
            name: name.to_string(),
            iterations,
            total_time,
            avg_time,
            ops_per_sec,
        }
    }

    /// Compare two implementations and return the faster one.
    pub fn compare<F1: FnMut(), F2: FnMut>(
        name_a: &str,
        name_b: &str,
        iterations: usize,
        mut a: F1,
        mut b: F2,
    ) -> (BenchmarkResult, BenchmarkResult, String) {
        let result_a = Self::bench(name_a, iterations, &mut a);
        let result_b = Self::bench(name_b, iterations, &mut b);

        let winner = if result_a.avg_time <= result_b.avg_time {
            name_a.to_string()
        } else {
            name_b.to_string()
        };

        (result_a, result_b, winner)
    }
}

/// Result of a complexity analysis.
#[derive(Debug, Clone)]
pub struct ComplexityAnalysis {
    pub name: String,
    pub measured_time_ns: u64,
    pub input_size: usize,
    pub estimated_complexity: String,
}

impl BenchmarkRunner {
    /// Measure execution time for a specific input size.
    pub fn measure<F: FnMut()>(name: &str, input_size: usize, mut f: F) -> ComplexityAnalysis {
        let start = Instant::now();
        f();
        let elapsed = start.elapsed();

        ComplexityAnalysis {
            name: name.to_string(),
            measured_time_ns: elapsed.as_nanos() as u64,
            input_size,
            estimated_complexity: String::new(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_benchmark_runner() {
        let result = BenchmarkRunner::bench("test_loop", 1000, || {
            let _ = (0..100).sum::<i64>();
        });
        assert_eq!(result.name, "test_loop");
        assert_eq!(result.iterations, 1000);
        assert!(result.ops_per_sec > 0.0);
    }

    #[test]
    fn test_compare() {
        let (a, b, winner) = BenchmarkRunner::compare(
            "fast",
            "slow",
            1000,
            || { /* fast */ },
            || {
                std::thread::sleep(Duration::from_millis(1));
            },
        );
        assert_eq!(winner, "fast");
    }
}
