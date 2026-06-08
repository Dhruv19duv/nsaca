//! Min-Max Heap implementation.
//!
//! A double-ended priority queue supporting O(log n) insert,
//! O(1) get_min/get_max, and O(log n) delete_min/delete_max.

/// A min-max heap data structure.
pub struct MinMaxHeap {
    data: Vec<i64>,
}

impl MinMaxHeap {
    /// Create an empty min-max heap.
    pub fn new() -> Self {
        MinMaxHeap { data: Vec::new() }
    }

    /// Create a min-max heap from an existing vector.
    pub fn from_vec(mut vec: Vec<i64>) -> Self {
        let mut heap = MinMaxHeap { data: vec };
        // Heapify in O(n)
        if heap.data.len() > 1 {
            for i in (0..heap.data.len() / 2).rev() {
                heap.sift_down(i);
            }
        }
        heap
    }

    /// Insert a value into the heap.
    pub fn push(&mut self, val: i64) {
        self.data.push(val);
        let idx = self.data.len() - 1;
        self.sift_up(idx);
    }

    /// Get the minimum value without removing it.
    pub fn peek_min(&self) -> Option<i64> {
        self.data.first().copied()
    }

    /// Get the maximum value without removing it.
    pub fn peek_max(&self) -> Option<i64> {
        if self.data.is_empty() {
            return None;
        }
        // Max is among the first-level children of root
        let last = self.data.len() - 1;
        let candidates = [0, 1.min(last), 2.min(last)];
        candidates
            .iter()
            .filter_map(|&i| self.data.get(i))
            .copied()
            .max()
    }

    /// Remove and return the minimum value.
    pub fn pop_min(&mut self) -> Option<i64> {
        if self.data.is_empty() {
            return None;
        }
        if self.data.len() == 1 {
            return self.data.pop();
        }
        let min = self.data[0];
        let last = self.data.pop().unwrap();
        self.data[0] = last;
        self.sift_down(0);
        Some(min)
    }

    /// Remove and return the maximum value.
    pub fn pop_max(&mut self) -> Option<i64> {
        if self.data.is_empty() {
            return None;
        }
        let last = self.data.len() - 1;
        if last == 0 {
            return self.data.pop();
        }
        // Find max among first-level children
        let max_idx = [1, 2]
            .iter()
            .filter(|&&i| i <= last)
            .max_by_key(|&&i| &self.data[i])
            .copied()
            .unwrap_or(0);
        let max = self.data[max_idx];
        self.data[max_idx] = self.data[last];
        self.data.pop();
        self.sift_down(max_idx);
        Some(max)
    }

    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    fn is_min_level(&self, idx: usize) -> bool {
        let level = (idx + 1).ilog2() as usize;
        level % 2 == 0
    }

    fn parent(&self, idx: usize) -> Option<usize> {
        if idx == 0 {
            None
        } else {
            Some((idx - 1) / 2)
        }
    }

    fn children(&self, idx: usize) -> Vec<usize> {
        let left = 2 * idx + 1;
        let right = 2 * idx + 2;
        let mut result = Vec::new();
        if left < self.data.len() {
            result.push(left);
        }
        if right < self.data.len() {
            result.push(right);
        }
        // Include grandchildren for min-max heap
        let mut grandchildren = Vec::new();
        for &c in &result.clone() {
            let gl = 2 * c + 1;
            let gr = 2 * c + 2;
            if gl < self.data.len() {
                grandchildren.push(gl);
            }
            if gr < self.data.len() {
                grandchildren.push(gr);
            }
        }
        result.extend(grandchildren);
        result
    }

    fn sift_up(&mut self, idx: usize) {
        if self.is_min_level(idx) {
            // On min level: if bigger than parent (max), swap, then sift up as max
            if let Some(p) = self.parent(idx) {
                if self.data[idx] > self.data[p] {
                    self.data.swap(idx, p);
                    self.sift_up_max(p);
                } else {
                    self.sift_up_min(idx);
                }
            }
        } else {
            // On max level: if smaller than parent (min), swap, then sift up as min
            if let Some(p) = self.parent(idx) {
                if self.data[idx] < self.data[p] {
                    self.data.swap(idx, p);
                    self.sift_up_min(p);
                } else {
                    self.sift_up_max(idx);
                }
            }
        }
    }

    fn sift_up_min(&mut self, mut idx: usize) {
        while let Some(gp) = self.parent(idx).and_then(|p| self.parent(p)) {
            if self.data[idx] < self.data[gp] {
                self.data.swap(idx, gp);
                idx = gp;
            } else {
                break;
            }
        }
    }

    fn sift_up_max(&mut self, mut idx: usize) {
        while let Some(gp) = self.parent(idx).and_then(|p| self.parent(p)) {
            if self.data[idx] > self.data[gp] {
                self.data.swap(idx, gp);
                idx = gp;
            } else {
                break;
            }
        }
    }

    fn sift_down(&mut self, idx: usize) {
        if self.is_min_level(idx) {
            self.sift_down_min(idx);
        } else {
            self.sift_down_max(idx);
        }
    }

    fn sift_down_min(&mut self, idx: usize) {
        let children = self.children(idx);
        if children.is_empty() {
            return;
        }
        // Find the minimum among children and grandchildren
        let min_child = *children
            .iter()
            .min_by_key(|&&i| &self.data[i])
            .unwrap();

        if min_child >= self.data.len() {
            return;
        }

        if self.data[min_child] < self.data[idx] {
            self.data.swap(idx, min_child);
            // If min_child is a grandchild, check if it needs to go up
            if !self.parent(min_child).map_or(false, |p| p == idx) {
                if let Some(p) = self.parent(min_child) {
                    if self.data[min_child] > self.data[p] {
                        self.data.swap(min_child, p);
                    }
                }
                self.sift_down_min(min_child);
            } else {
                self.sift_down_min(min_child);
            }
        }
    }

    fn sift_down_max(&mut self, idx: usize) {
        let children = self.children(idx);
        if children.is_empty() {
            return;
        }
        let max_child = *children
            .iter()
            .max_by_key(|&&i| &self.data[i])
            .unwrap();

        if max_child >= self.data.len() {
            return;
        }

        if self.data[max_child] > self.data[idx] {
            self.data.swap(idx, max_child);
            if !self.parent(max_child).map_or(false, |p| p == idx) {
                if let Some(p) = self.parent(max_child) {
                    if self.data[max_child] < self.data[p] {
                        self.data.swap(max_child, p);
                    }
                }
                self.sift_down_max(max_child);
            } else {
                self.sift_down_max(max_child);
            }
        }
    }
}

impl Default for MinMaxHeap {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_min_max_heap() {
        let mut heap = MinMaxHeap::new();
        heap.push(5);
        heap.push(3);
        heap.push(8);
        heap.push(1);
        heap.push(9);

        assert_eq!(heap.pop_min(), Some(1));
        assert_eq!(heap.pop_max(), Some(9));
        assert_eq!(heap.pop_min(), Some(3));
        assert_eq!(heap.pop_max(), Some(8));
        assert_eq!(heap.pop_min(), Some(5));
        assert!(heap.is_empty());
    }
}
