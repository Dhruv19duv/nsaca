//! Segment Tree implementation with lazy propagation.
//!
//! Supports range queries and range updates in O(log n) time.
//! Useful for interval-based problems like range sum, range min/max.

/// A segment tree supporting range queries and lazy propagation updates.
pub struct SegmentTree {
    tree: Vec<i64>,
    lazy: Vec<i64>,
    n: usize,
}

impl SegmentTree {
    /// Build a segment tree from an array of values.
    pub fn new(data: &[i64]) -> Self {
        let n = data.len();
        let mut st = SegmentTree {
            tree: vec![0; 4 * n],
            lazy: vec![0; 4 * n],
            n,
        };
        if n > 0 {
            st.build(data, 1, 0, n - 1);
        }
        st
    }

    fn build(&mut self, data: &[i64], node: usize, start: usize, end: usize) {
        if start == end {
            self.tree[node] = data[start];
            return;
        }
        let mid = (start + end) / 2;
        self.build(data, 2 * node, start, mid);
        self.build(data, 2 * node + 1, mid + 1, end);
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1];
    }

    /// Push lazy propagation values down to children.
    fn push(&mut self, node: usize, start: usize, end: usize) {
        if self.lazy[node] != 0 {
            let mid = (start + end) / 2;
            self.apply_lazy(2 * node, start, mid, self.lazy[node]);
            self.apply_lazy(2 * node + 1, mid + 1, end, self.lazy[node]);
            self.lazy[node] = 0;
        }
    }

    fn apply_lazy(&mut self, node: usize, start: usize, end: usize, val: i64) {
        self.tree[node] += val * ((end - start + 1) as i64);
        self.lazy[node] += val;
    }

    /// Update range [l, r] by adding `val` to each element.
    pub fn update_range(&mut self, l: usize, r: usize, val: i64) {
        self.update_range_rec(1, 0, self.n - 1, l, r, val);
    }

    fn update_range_rec(
        &mut self,
        node: usize,
        start: usize,
        end: usize,
        l: usize,
        r: usize,
        val: i64,
    ) {
        if r < start || end < l {
            return;
        }
        if l <= start && end <= r {
            self.apply_lazy(node, start, end, val);
            return;
        }
        self.push(node, start, end);
        let mid = (start + end) / 2;
        self.update_range_rec(2 * node, start, mid, l, r, val);
        self.update_range_rec(2 * node + 1, mid + 1, end, l, r, val);
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1];
    }

    /// Query sum over range [l, r].
    pub fn query(&mut self, l: usize, r: usize) -> i64 {
        self.query_rec(1, 0, self.n - 1, l, r)
    }

    fn query_rec(&mut self, node: usize, start: usize, end: usize, l: usize, r: usize) -> i64 {
        if r < start || end < l {
            return 0;
        }
        if l <= start && end <= r {
            return self.tree[node];
        }
        self.push(node, start, end);
        let mid = (start + end) / 2;
        self.query_rec(2 * node, start, mid, l, r)
            + self.query_rec(2 * node + 1, mid + 1, end, l, r)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_segment_tree_basic() {
        let data = vec![1, 3, 5, 7, 9, 11];
        let mut st = SegmentTree::new(&data);
        assert_eq!(st.query(0, 2), 9);  // 1 + 3 + 5
        assert_eq!(st.query(1, 4), 24); // 3 + 5 + 7 + 9
        assert_eq!(st.query(0, 5), 36); // sum of all
    }

    #[test]
    fn test_segment_tree_update() {
        let data = vec![1, 2, 3, 4, 5];
        let mut st = SegmentTree::new(&data);
        st.update_range(1, 3, 10); // add 10 to [1,3]
        assert_eq!(st.query(0, 4), 1 + 12 + 13 + 14 + 5);
    }
}
