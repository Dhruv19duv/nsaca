//! Suffix Array implementation.
//!
//! Space-efficient representation of all suffixes of a string.
//! Useful for string matching, longest common substring, and pattern searching.

/// Suffix array with LCP (Longest Common Prefix) array.
pub struct SuffixArray {
    sa: Vec<usize>,
    rank: Vec<usize>,
    lcp: Vec<usize>,
    text: Vec<u8>,
}

impl SuffixArray {
    /// Build suffix array from text using the O(n log n) algorithm.
    pub fn new(text: &[u8]) -> Self {
        let n = text.len();
        if n == 0 {
            return SuffixArray {
                sa: Vec::new(),
                rank: Vec::new(),
                lcp: Vec::new(),
                text: Vec::new(),
            };
        }

        let mut sa: Vec<usize> = (0..n).collect();
        let mut rank: Vec<usize> = text.iter().map(|&b| b as usize).collect();
        let mut tmp = vec![0usize; n];
        let mut k = 1;

        while k < n {
            // Comparator: rank[i] vs rank[i+k]
            let cmp = |a: &usize, b: &usize| -> std::cmp::Ordering {
                rank[*a]
                    .cmp(&rank[*b])
                    .then_with(|| rank.get(a + k).unwrap_or(&0).cmp(rank.get(b + k).unwrap_or(&0)))
            };
            sa.sort_by(cmp);

            tmp[sa[0]] = 0;
            for i in 1..n {
                tmp[sa[i]] = tmp[sa[i - 1]]
                    + if cmp(&sa[i - 1], &sa[i]) == std::cmp::Ordering::Less {
                        1
                    } else {
                        0
                    };
            }
            rank.clone_from_slice(&tmp);
            if rank[sa[n - 1]] == n - 1 {
                break;
            }
            k *= 2;
        }

        // Build LCP array using Kasai's algorithm
        let mut lcp = vec![0usize; n];
        let mut inv_sa = vec![0usize; n];
        for i in 0..n {
            inv_sa[sa[i]] = i;
        }
        let mut k_lcp = 0usize;
        for i in 0..n {
            if inv_sa[i] > 0 {
                let j = sa[inv_sa[i] - 1];
                while i + k_lcp < n && j + k_lcp < n && text[i + k_lcp] == text[j + k_lcp] {
                    k_lcp += 1;
                }
                lcp[inv_sa[i]] = k_lcp;
                if k_lcp > 0 {
                    k_lcp -= 1;
                }
            } else {
                k_lcp = 0;
            }
        }

        SuffixArray {
            sa,
            rank,
            lcp,
            text: text.to_vec(),
        }
    }

    /// Get the suffix array.
    pub fn suffix_array(&self) -> &[usize] {
        &self.sa
    }

    /// Get the LCP array.
    pub fn lcp_array(&self) -> &[usize] {
        &self.lcp
    }

    /// Binary search for a pattern in the text. Returns starting indices.
    pub fn search(&self, pattern: &[u8]) -> Vec<usize> {
        let n = self.text.len();
        let m = pattern.len();
        let mut results = Vec::new();

        // Find leftmost match
        let mut lo = 0;
        let mut hi = n;
        while lo < hi {
            let mid = (lo + hi) / 2;
            let suffix = &self.text[self.sa[mid]..];
            let cmp_len = m.min(suffix.len());
            if suffix[..cmp_len] < pattern[..cmp_len] {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        let start = lo;

        // Find rightmost match
        lo = start;
        hi = n;
        while lo < hi {
            let mid = (lo + hi) / 2;
            let suffix = &self.text[self.sa[mid]..];
            let cmp_len = m.min(suffix.len());
            if suffix[..cmp_len] <= pattern[..cmp_len.min(pattern.len())] {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        let end = lo;

        for i in start..end {
            let pos = self.sa[i];
            if pos + m <= n && &self.text[pos..pos + m] == pattern {
                results.push(pos);
            }
        }
        results.sort();
        results
    }

    /// Length of the text.
    pub fn len(&self) -> usize {
        self.text.len()
    }

    /// Check if the suffix array is empty.
    pub fn is_empty(&self) -> bool {
        self.text.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_suffix_array_basic() {
        let sa = SuffixArray::new(b"banana");
        // Suffixes sorted: a(5), ana(3), anana(1), banana(0), na(4), nana(2)
        assert_eq!(sa.suffix_array(), &[5, 3, 1, 0, 4, 2]);
    }

    #[test]
    fn test_suffix_array_search() {
        let sa = SuffixArray::new(b"mississippi");
        let results = sa.search(b"issi");
        assert_eq!(results, vec![1]);
    }
}
