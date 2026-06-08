//! Trie (prefix tree) implementation.
//!
//! Supports insertion, search, prefix matching, and autocomplete.
//! Optimized for memory efficiency with compact node representation.

use hashbrown::HashMap;

/// A trie node.
struct TrieNode {
    children: HashMap<char, TrieNode>,
    is_end: bool,
    count: usize, // number of words passing through this node
}

/// Trie data structure for prefix-based operations.
pub struct Trie {
    root: TrieNode,
    size: usize,
}

impl Trie {
    /// Create a new empty trie.
    pub fn new() -> Self {
        Trie {
            root: TrieNode {
                children: HashMap::new(),
                is_end: false,
                count: 0,
            },
            size: 0,
        }
    }

    /// Insert a word into the trie.
    pub fn insert(&mut self, word: &str) {
        let mut current = &mut self.root;
        for ch in word.chars() {
            current.count += 1;
            current = current
                .children
                .entry(ch)
                .or_insert_with(|| TrieNode {
                    children: HashMap::new(),
                    is_end: false,
                    count: 0,
                });
        }
        if !current.is_end {
            self.size += 1;
        }
        current.is_end = true;
        current.count += 1;
    }

    /// Search for an exact word in the trie.
    pub fn search(&self, word: &str) -> bool {
        self.find_node(word)
            .map(|node| node.is_end)
            .unwrap_or(false)
    }

    /// Check if any word starts with the given prefix.
    pub fn starts_with(&self, prefix: &str) -> bool {
        self.find_node(prefix).is_some()
    }

    /// Get autocomplete suggestions for a given prefix.
    pub fn autocomplete(&self, prefix: &str, max_results: usize) -> Vec<String> {
        let mut results = Vec::new();
        if let Some(node) = self.find_node(prefix) {
            self.collect_words(node, &mut prefix.chars().collect(), &mut results, max_results);
        }
        results
    }

    /// Get the number of words in the trie.
    pub fn len(&self) -> usize {
        self.size
    }

    /// Check if the trie is empty.
    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    fn find_node(&self, prefix: &str) -> Option<&TrieNode> {
        let mut current = &self.root;
        for ch in prefix.chars() {
            current = current.children.get(&ch)?;
        }
        Some(current)
    }

    fn collect_words(
        &self,
        node: &TrieNode,
        current: &mut Vec<char>,
        results: &mut Vec<String>,
        max_results: usize,
    ) {
        if results.len() >= max_results {
            return;
        }
        if node.is_end {
            results.push(current.iter().collect());
        }
        for (ch, child) in &node.children {
            current.push(*ch);
            self.collect_words(child, current, results, max_results);
            current.pop();
        }
    }
}

impl Default for Trie {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_trie_insert_search() {
        let mut trie = Trie::new();
        trie.insert("hello");
        trie.insert("help");
        trie.insert("world");

        assert!(trie.search("hello"));
        assert!(trie.search("help"));
        assert!(trie.search("world"));
        assert!(!trie.search("hell"));
        assert!(!trie.search("helloo"));
    }

    #[test]
    fn test_trie_prefix() {
        let mut trie = Trie::new();
        trie.insert("hello");
        trie.insert("help");

        assert!(trie.starts_with("hel"));
        assert!(!trie.starts_with("wor"));
    }

    #[test]
    fn test_trie_autocomplete() {
        let mut trie = Trie::new();
        trie.insert("hello");
        trie.insert("help");
        trie.insert("hero");

        let suggestions = trie.autocomplete("hel", 10);
        assert_eq!(suggestions.len(), 2);
        assert!(suggestions.contains(&"hello".to_string()));
        assert!(suggestions.contains(&"help".to_string()));
    }
}
