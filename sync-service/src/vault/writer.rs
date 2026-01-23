// Writer module for creating and updating markdown files with atomic operations

use crate::vault::parser::parse_markdown_file;
use crate::vault::template::ItemMetadata;
use anyhow::Result;
use std::fs;
use std::io::Write;
use std::path::Path;
use tempfile::NamedTempFile;

/// Write markdown file with frontmatter atomically
///
/// Creates or overwrites a markdown file with YAML frontmatter and content.
/// Uses atomic write operations (temp file + rename) to prevent partial writes.
///
/// # Arguments
///
/// * `file_path` - Path to write the markdown file
/// * `metadata` - Item metadata for YAML frontmatter
/// * `content` - Markdown content body
///
/// # Returns
///
/// `Ok(())` if file written successfully
///
/// # Errors
///
/// Returns an error if:
/// - Cannot serialize metadata to YAML
/// - Cannot create parent directories
/// - Cannot write to file
/// - I/O error occurs
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::writer::write_markdown_file;
/// use noosphere_sync::vault::template::ItemMetadata;
/// use std::path::Path;
/// use uuid::Uuid;
/// use chrono::Utc;
///
/// let metadata = ItemMetadata {
///     id: Uuid::new_v4(),
///     title: "My Note".to_string(),
///     category: "Ideas".to_string(),
///     subcategory: None,
///     tags: vec!["brainstorm".to_string()],
///     created: Utc::now().to_rfc3339(),
///     modified: Utc::now().to_rfc3339(),
///     state: "active".to_string(),
///     confidence: Some(0.9),
/// };
///
/// write_markdown_file(
///     Path::new("/tmp/my-note.md"),
///     &metadata,
///     "# My Note\n\nContent goes here."
/// )?;
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn write_markdown_file(file_path: &Path, metadata: &ItemMetadata, content: &str) -> Result<()> {
    // Serialize metadata to YAML
    let yaml = serde_yaml::to_string(metadata)
        .map_err(|e| anyhow::anyhow!("Failed to serialize metadata: {}", e))?;

    // Combine frontmatter + content
    let markdown = format!("---\n{}---\n\n{}", yaml, content);

    // Atomic write: temp file + rename
    atomic_write(file_path, &markdown)?;

    Ok(())
}

/// Atomic write using temp file and rename
///
/// Writes content to a temporary file in the same directory, then atomically
/// renames it to the target path. This prevents partial writes and race conditions.
///
/// # Arguments
///
/// * `file_path` - Target file path
/// * `content` - Content to write
///
/// # Returns
///
/// `Ok(())` if write successful
///
/// # Errors
///
/// Returns an error if I/O operations fail
fn atomic_write(file_path: &Path, content: &str) -> Result<()> {
    // Create parent directory if needed
    if let Some(parent) = file_path.parent() {
        fs::create_dir_all(parent)?;
    }

    // Write to temp file in same directory (ensures atomic rename)
    let dir = file_path.parent().unwrap_or_else(|| Path::new("."));
    let mut temp_file = NamedTempFile::new_in(dir)?;
    temp_file.write_all(content.as_bytes())?;
    temp_file.flush()?;

    // Atomic rename (POSIX guarantee)
    temp_file.persist(file_path)?;

    Ok(())
}

/// Update only the frontmatter of an existing markdown file
///
/// Reads the file, applies updates to the metadata, and writes it back
/// without modifying the content body. Uses atomic operations.
///
/// # Arguments
///
/// * `file_path` - Path to the markdown file
/// * `updates` - Closure that modifies the metadata
///
/// # Returns
///
/// `Ok(())` if update successful
///
/// # Errors
///
/// Returns an error if:
/// - File cannot be read
/// - Frontmatter is invalid
/// - Cannot write updated file
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::writer::update_frontmatter;
/// use std::path::Path;
/// use chrono::Utc;
///
/// // Update only the category, leaving content unchanged
/// update_frontmatter(Path::new("/tmp/note.md"), |metadata| {
///     metadata.category = "Projects".to_string();
///     metadata.modified = Utc::now().to_rfc3339();
/// })?;
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn update_frontmatter(file_path: &Path, updates: impl Fn(&mut ItemMetadata)) -> Result<()> {
    // Read existing file
    let (mut metadata, content) = parse_markdown_file(file_path)?;

    // Apply updates
    updates(&mut metadata);

    // Write back with updated metadata
    write_markdown_file(file_path, &metadata, &content)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use tempfile::tempdir;
    use uuid::Uuid;

    fn create_test_metadata() -> ItemMetadata {
        ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test Item".to_string(),
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec!["test".to_string()],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: Some(0.9),
        }
    }

    #[test]
    fn test_write_markdown_file() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("test.md");

        let metadata = create_test_metadata();
        let content = "# Test Item\n\nThis is the content.";

        write_markdown_file(&file_path, &metadata, content)?;

        // Verify file exists
        assert!(file_path.exists());

        // Verify content
        let written = fs::read_to_string(&file_path)?;
        assert!(written.starts_with("---\n"));
        assert!(written.contains("title: Test Item"));
        assert!(written.contains("category: Ideas"));
        assert!(written.contains("# Test Item"));
        assert!(written.contains("This is the content"));

        Ok(())
    }

    #[test]
    fn test_write_creates_parent_dirs() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir
            .path()
            .join("subdir")
            .join("nested")
            .join("test.md");

        let metadata = create_test_metadata();
        write_markdown_file(&file_path, &metadata, "Content")?;

        // Verify file and parent directories created
        assert!(file_path.exists());
        assert!(file_path.parent().unwrap().exists());

        Ok(())
    }

    #[test]
    fn test_atomic_write() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("atomic.md");

        // Write content atomically
        atomic_write(&file_path, "Test content")?;

        // Verify file exists and content is correct
        assert!(file_path.exists());
        let content = fs::read_to_string(&file_path)?;
        assert_eq!(content, "Test content");

        // Overwrite with new content
        atomic_write(&file_path, "Updated content")?;
        let content = fs::read_to_string(&file_path)?;
        assert_eq!(content, "Updated content");

        Ok(())
    }

    #[test]
    fn test_update_frontmatter() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("update.md");

        // Create initial file
        let metadata = create_test_metadata();
        let original_content = "# Original Heading\n\nOriginal content body.";
        write_markdown_file(&file_path, &metadata, original_content)?;

        // Update frontmatter
        update_frontmatter(&file_path, |meta| {
            meta.category = "Projects".to_string();
            meta.tags.push("updated".to_string());
        })?;

        // Verify frontmatter updated
        let (updated_meta, content) = parse_markdown_file(&file_path)?;
        assert_eq!(updated_meta.category, "Projects");
        assert!(updated_meta.tags.contains(&"updated".to_string()));
        assert_eq!(updated_meta.title, "Test Item"); // Unchanged

        // Verify content unchanged
        assert!(content.contains("Original Heading"));
        assert!(content.contains("Original content body"));

        Ok(())
    }

    #[test]
    fn test_update_frontmatter_preserves_content() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("preserve.md");

        let metadata = create_test_metadata();
        let complex_content = r#"# Heading

Paragraph with **bold** and *italic*.

- List item 1
- List item 2

```rust
fn code_block() {
    println!("preserved");
}
```

## Subheading

More content here."#;

        write_markdown_file(&file_path, &metadata, complex_content)?;

        // Update frontmatter
        update_frontmatter(&file_path, |meta| {
            meta.state = "archived".to_string();
        })?;

        // Verify content perfectly preserved
        let (updated_meta, content) = parse_markdown_file(&file_path)?;
        assert_eq!(updated_meta.state, "archived");
        assert_eq!(content.trim(), complex_content.trim());

        Ok(())
    }

    #[test]
    fn test_write_unicode_content() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("unicode.md");

        let mut metadata = create_test_metadata();
        metadata.title = "Unicode Test 世界".to_string();

        let content = "# Unicode\n\nHello, 世界! 🌍\n\nこんにちは";

        write_markdown_file(&file_path, &metadata, content)?;

        // Verify unicode preserved
        let (read_meta, read_content) = parse_markdown_file(&file_path)?;
        assert_eq!(read_meta.title, "Unicode Test 世界");
        assert!(read_content.contains("Hello, 世界! 🌍"));
        assert!(read_content.contains("こんにちは"));

        Ok(())
    }

    #[test]
    fn test_write_overwrites_existing() -> Result<()> {
        let temp_dir = tempdir()?;
        let file_path = temp_dir.path().join("overwrite.md");

        // Write initial content
        let metadata1 = create_test_metadata();
        write_markdown_file(&file_path, &metadata1, "Original")?;

        // Overwrite with new content
        let mut metadata2 = create_test_metadata();
        metadata2.title = "Updated Title".to_string();
        write_markdown_file(&file_path, &metadata2, "New content")?;

        // Verify overwritten
        let (read_meta, read_content) = parse_markdown_file(&file_path)?;
        assert_eq!(read_meta.title, "Updated Title");
        assert!(read_content.contains("New content"));
        assert!(!read_content.contains("Original"));

        Ok(())
    }
}
