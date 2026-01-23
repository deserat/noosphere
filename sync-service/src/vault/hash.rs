// Content hashing module for detecting file changes

use anyhow::Result;
use sha2::{Digest, Sha256};
use std::fs;
use std::path::Path;

/// Compute SHA-256 hash of string content
///
/// Returns a hexadecimal string representation of the hash.
/// Used for detecting content changes and sync conflict detection.
///
/// # Arguments
///
/// * `content` - The string content to hash
///
/// # Returns
///
/// A 64-character hexadecimal string (SHA-256 hash)
///
/// # Example
///
/// ```
/// use noosphere_sync::vault::hash::compute_content_hash;
///
/// let hash1 = compute_content_hash("Hello, world!");
/// let hash2 = compute_content_hash("Hello, world!");
/// assert_eq!(hash1, hash2); // Same content = same hash
///
/// let hash3 = compute_content_hash("Different content");
/// assert_ne!(hash1, hash3); // Different content = different hash
/// ```
pub fn compute_content_hash(content: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(content.as_bytes());
    format!("{:x}", hasher.finalize())
}

/// Compute SHA-256 hash of a file's contents
///
/// Reads the entire file and computes its SHA-256 hash.
/// Returns an error if the file cannot be read.
///
/// # Arguments
///
/// * `file_path` - Path to the file to hash
///
/// # Returns
///
/// A 64-character hexadecimal string (SHA-256 hash)
///
/// # Errors
///
/// Returns an error if:
/// - File does not exist
/// - File cannot be read
/// - I/O error occurs
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::hash::compute_file_hash;
/// use std::path::Path;
///
/// let hash = compute_file_hash(Path::new("/tmp/test.md"))?;
/// println!("File hash: {}", hash);
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn compute_file_hash(file_path: &Path) -> Result<String> {
    let content = fs::read(file_path)?;
    let mut hasher = Sha256::new();
    hasher.update(&content);
    Ok(format!("{:x}", hasher.finalize()))
}

/// Check if file content has changed since cached hash
///
/// Compares the current file hash with a previously cached hash.
/// Returns `true` if the content has changed (or if no cached hash provided).
///
/// # Arguments
///
/// * `file_path` - Path to the file to check
/// * `cached_hash` - Optional previously computed hash
///
/// # Returns
///
/// - `true` if content has changed (or no cached hash available)
/// - `false` if content is unchanged
///
/// # Errors
///
/// Returns an error if file cannot be read.
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::hash::{compute_file_hash, has_content_changed};
/// use std::path::Path;
///
/// let path = Path::new("/tmp/test.md");
/// let cached = compute_file_hash(path)?;
///
/// // ... file is modified externally (e.g., in Obsidian) ...
///
/// if has_content_changed(path, Some(&cached))? {
///     println!("File was modified externally!");
/// }
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn has_content_changed(file_path: &Path, cached_hash: Option<&str>) -> Result<bool> {
    let current_hash = compute_file_hash(file_path)?;

    match cached_hash {
        Some(cached) => Ok(current_hash != cached),
        None => Ok(true), // No cached hash, assume changed
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_compute_content_hash() {
        let content = "Hello, world!";
        let hash = compute_content_hash(content);

        // SHA-256 hash should be 64 hex characters
        assert_eq!(hash.len(), 64);

        // Hash should be deterministic
        let hash2 = compute_content_hash(content);
        assert_eq!(hash, hash2);
    }

    #[test]
    fn test_hash_deterministic() {
        let content = "Test content for hashing";
        let hash1 = compute_content_hash(content);
        let hash2 = compute_content_hash(content);
        let hash3 = compute_content_hash(content);

        assert_eq!(hash1, hash2);
        assert_eq!(hash2, hash3);
    }

    #[test]
    fn test_different_content_different_hash() {
        let hash1 = compute_content_hash("Content A");
        let hash2 = compute_content_hash("Content B");

        assert_ne!(hash1, hash2);
    }

    #[test]
    fn test_compute_file_hash() -> Result<()> {
        // Create temporary file
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test file content")?;
        temp_file.flush()?;

        // Compute hash
        let hash = compute_file_hash(temp_file.path())?;

        // Should be 64 hex characters
        assert_eq!(hash.len(), 64);

        // Should match hash of content
        let content_hash = compute_content_hash("Test file content");
        assert_eq!(hash, content_hash);

        Ok(())
    }

    #[test]
    fn test_has_content_changed_no_cache() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Initial content")?;
        temp_file.flush()?;

        // No cached hash - should report changed
        assert!(has_content_changed(temp_file.path(), None)?);

        Ok(())
    }

    #[test]
    fn test_has_content_changed_unchanged() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Static content")?;
        temp_file.flush()?;

        // Compute initial hash
        let cached_hash = compute_file_hash(temp_file.path())?;

        // Content hasn't changed
        assert!(!has_content_changed(temp_file.path(), Some(&cached_hash))?);

        Ok(())
    }

    #[test]
    fn test_has_content_changed_modified() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Initial content")?;
        temp_file.flush()?;

        // Compute initial hash
        let cached_hash = compute_file_hash(temp_file.path())?;

        // Modify file
        temp_file.reopen()?;
        write!(temp_file, "Modified content")?;
        temp_file.flush()?;

        // Content has changed
        assert!(has_content_changed(temp_file.path(), Some(&cached_hash))?);

        Ok(())
    }

    #[test]
    fn test_unicode_content() {
        // Test with unicode characters
        let content = "Hello, 世界! 🌍";
        let hash1 = compute_content_hash(content);
        let hash2 = compute_content_hash(content);

        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 64);
    }
}
