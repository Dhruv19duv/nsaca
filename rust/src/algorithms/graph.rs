//! Graph algorithms implementation.
//!
//! Provides shortest path, connectivity, topological sort, and graph traversal
//! algorithms optimized for the NSACA dependency graph analysis.

use hashbrown::{HashMap, HashSet};
use std::collections::VecDeque;

/// A weighted directed graph.
pub struct Graph {
    pub n: usize,
    pub adj: Vec<Vec<(usize, f64)>>, // (neighbor, weight)
}

impl Graph {
    /// Create a graph with `n` nodes.
    pub fn new(n: usize) -> Self {
        Graph {
            n,
            adj: vec![Vec::new(); n],
        }
    }

    /// Add a directed edge from `from` to `to` with weight `w`.
    pub fn add_edge(&mut self, from: usize, to: usize, w: f64) {
        self.adj[from].push((to, w));
    }

    /// Dijkstra's shortest path from `src`. Returns `None` if unreachable.
    pub fn dijkstra(&self, src: usize) -> Vec<Option<f64>> {
        let mut dist = vec![f64::INFINITY; self.n];
        dist[src] = 0.0;
        // Simple binary heap approach using sorted vec (swap-remove based)
        let mut heap: Vec<(f64, usize)> = vec![(0.0, src)];

        while let Some((d, u)) = heap.pop() {
            if d > dist[u] {
                continue;
            }
            for &(v, w) in &self.adj[u] {
                let nd = d + w;
                if nd < dist[v] {
                    dist[v] = nd;
                    heap.push((nd, v));
                    // Keep heap somewhat sorted
                    heap.sort_unstable_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
                }
            }
        }

        dist.into_iter()
            .map(|d| if d.is_infinite() { None } else { Some(d) })
            .collect()
    }

    /// Bellman-Ford shortest path from `src`. Handles negative weights.
    /// Returns `(distances, has_negative_cycle)`.
    pub fn bellman_ford(&self, src: usize) -> (Vec<Option<f64>>, bool) {
        let mut dist = vec![f64::INFINITY; self.n];
        dist[src] = 0.0;

        // Collect all edges
        let mut edges: Vec<(usize, usize, f64)> = Vec::new();
        for u in 0..self.n {
            for &(v, w) in &self.adj[u] {
                edges.push((u, v, w));
            }
        }

        // Relax edges n-1 times
        for _ in 0..self.n - 1 {
            let mut updated = false;
            for &(u, v, w) in &edges {
                if dist[u] + w < dist[v] {
                    dist[v] = dist[u] + w;
                    updated = true;
                }
            }
            if !updated {
                break;
            }
        }

        // Check for negative cycle
        let mut has_neg_cycle = false;
        for &(u, v, w) in &edges {
            if dist[u] + w < dist[v] {
                has_neg_cycle = true;
                break;
            }
        }

        let result = dist
            .into_iter()
            .map(|d| if d.is_infinite() { None } else { Some(d) })
            .collect();
        (result, has_neg_cycle)
    }

    /// Topological sort using Kahn's algorithm.
    /// Returns `None` if the graph has a cycle.
    pub fn topological_sort(&self) -> Option<Vec<usize>> {
        let mut in_degree = vec![0usize; self.n];
        for u in 0..self.n {
            for &(v, _) in &self.adj[u] {
                in_degree[v] += 1;
            }
        }

        let mut queue: VecDeque<usize> = VecDeque::new();
        for i in 0..self.n {
            if in_degree[i] == 0 {
                queue.push_back(i);
            }
        }

        let mut order = Vec::new();
        while let Some(u) = queue.pop_front() {
            order.push(u);
            for &(v, _) in &self.adj[u] {
                in_degree[v] -= 1;
                if in_degree[v] == 0 {
                    queue.push_back(v);
                }
            }
        }

        if order.len() == self.n {
            Some(order)
        } else {
            None // cycle exists
        }
    }

    /// BFS shortest path in unweighted graph.
    pub fn bfs(&self, src: usize) -> Vec<Option<usize>> {
        let mut dist = vec![None; self.n];
        let mut queue = VecDeque::new();
        dist[src] = Some(0);
        queue.push_back(src);

        while let Some(u) = queue.pop_front() {
            let d = dist[u].unwrap();
            for &(v, _) in &self.adj[u] {
                if dist[v].is_none() {
                    dist[v] = Some(d + 1);
                    queue.push_back(v);
                }
            }
        }
        dist
    }

    /// DFS-based cycle detection.
    pub fn has_cycle(&self) -> bool {
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();

        for i in 0..self.n {
            if !visited.contains(&i) {
                if self.dfs_cycle(i, &mut visited, &mut rec_stack) {
                    return true;
                }
            }
        }
        false
    }

    fn dfs_cycle(&self, u: usize, visited: &mut HashSet<usize>, rec_stack: &mut HashSet<usize>) -> bool {
        visited.insert(u);
        rec_stack.insert(u);

        for &(v, _) in &self.adj[u] {
            if !visited.contains(&v) {
                if self.dfs_cycle(v, visited, rec_stack) {
                    return true;
                }
            } else if rec_stack.contains(&v) {
                return true;
            }
        }

        rec_stack.remove(&u);
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dijkstra() {
        let mut g = Graph::new(4);
        g.add_edge(0, 1, 1.0);
        g.add_edge(1, 2, 2.0);
        g.add_edge(0, 2, 10.0);
        g.add_edge(2, 3, 1.0);

        let dist = g.dijkstra(0);
        assert_eq!(dist[0], Some(0.0));
        assert_eq!(dist[1], Some(1.0));
        assert_eq!(dist[2], Some(3.0));
        assert_eq!(dist[3], Some(4.0));
    }

    #[test]
    fn test_topological_sort() {
        let mut g = Graph::new(4);
        g.add_edge(0, 1, 1.0);
        g.add_edge(0, 2, 1.0);
        g.add_edge(1, 3, 1.0);
        g.add_edge(2, 3, 1.0);

        let order = g.topological_sort().unwrap();
        // 0 must come before 1 and 2, which must come before 3
        assert!(order.iter().position(|&x| x == 0).unwrap()
            < order.iter().position(|&x| x == 1).unwrap());
        assert!(order.iter().position(|&x| x == 1).unwrap()
            < order.iter().position(|&x| x == 3).unwrap());
    }

    #[test]
    fn test_cycle_detection() {
        let mut g = Graph::new(3);
        g.add_edge(0, 1, 1.0);
        g.add_edge(1, 2, 1.0);
        assert!(!g.has_cycle());

        g.add_edge(2, 0, 1.0);
        assert!(g.has_cycle());
    }
}
