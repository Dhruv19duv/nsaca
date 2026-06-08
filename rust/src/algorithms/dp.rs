//! Dynamic programming algorithms.
//!
//! Provides common DP patterns: knapsack, LIS, edit distance, and matrix chain.

/// 0/1 Knapsack problem solver.
/// Returns the maximum value achievable with given capacity.
pub fn knapsack_01(weights: &[usize], values: &[usize], capacity: usize) -> usize {
    let n = weights.len();
    let mut dp = vec![vec![0usize; capacity + 1]; n + 1];

    for i in 1..=n {
        let w = weights[i - 1];
        let v = values[i - 1];
        for c in 0..=capacity {
            dp[i][c] = dp[i - 1][c];
            if w <= c {
                dp[i][c] = dp[i][c].max(dp[i - 1][c - w] + v);
            }
        }
    }

    dp[n][capacity]
}

/// Longest Increasing Subsequence length. O(n log n).
pub fn lis_length(arr: &[i64]) -> usize {
    if arr.is_empty() {
        return 0;
    }
    let mut tails: Vec<i64> = Vec::new();

    for &val in arr {
        let pos = tails.partition_point(|&x| x < val);
        if pos == tails.len() {
            tails.push(val);
        } else {
            tails[pos] = val;
        }
    }

    tails.len()
}

/// Edit distance (Levenshtein distance) between two strings.
pub fn edit_distance(a: &[u8], b: &[u8]) -> usize {
    let m = a.len();
    let n = b.len();
    let mut dp = vec![vec![0usize; n + 1]; m + 1];

    for i in 0..=m {
        dp[i][0] = i;
    }
    for j in 0..=n {
        dp[0][j] = j;
    }

    for i in 1..=m {
        for j in 1..=n {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            dp[i][j] = (dp[i - 1][j] + 1)
                .min(dp[i][j - 1] + 1)
                .min(dp[i - 1][j - 1] + cost);
        }
    }

    dp[m][n]
}

/// Matrix chain multiplication: minimum scalar multiplications.
pub fn matrix_chain_order(dims: &[usize]) -> usize {
    let n = dims.len() - 1;
    if n == 0 {
        return 0;
    }
    let mut dp = vec![vec![0usize; n]; n];

    for len in 2..=n {
        for i in 0..=n - len {
            let j = i + len - 1;
            dp[i][j] = usize::MAX;
            for k in i..j {
                let cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1];
                dp[i][j] = dp[i][j].min(cost);
            }
        }
    }

    dp[0][n - 1]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_knapsack() {
        let weights = vec![2, 3, 4, 5];
        let values = vec![3, 4, 5, 6];
        assert_eq!(knapsack_01(&weights, &values, 5), 7); // items 0+1
    }

    #[test]
    fn test_lis() {
        assert_eq!(lis_length(&[10, 9, 2, 5, 3, 7, 101, 18]), 4);
    }

    #[test]
    fn test_edit_distance() {
        assert_eq!(edit_distance(b"kitten", b"sitting"), 3);
    }

    #[test]
    fn test_matrix_chain() {
        // A(10x30), B(30x5), C(5x60)
        // ABC: (10*30*5) + (10*5*60) = 1500 + 3000 = 4500
        // A(BC): (30*5*60) + (10*30*60) = 9000 + 18000 = 27000
        // Wait, optimal is 1500 + 3000 = 4500
        assert_eq!(matrix_chain_order(&[10, 30, 5, 60]), 4500);
    }
}
