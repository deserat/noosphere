// Parser module for reading markdown files with YAML frontmatter

use crate::vault::template::ItemMetadata;
use anyhow::Result;
use gray_matter::{engine::YAML, Matter};
use std::fs;
use std::path::Path;

/// Parse markdown file with YAML frontmatter
///
/// Reads a markdown file and extracts both the YAML frontmatter metadata
/// and the markdown content body.
///
/// # Arguments
///
/// * `file_path` - Path to the markdown file
///
/// # Returns
///
/// A tuple of `(ItemMetadata, String)` containing:
/// - Parsed frontmatter metadata
/// - Markdown content body (without frontmatter)
///
/// # Errors
///
/// Returns an error if:
/// - File cannot be read
/// - YAML frontmatter is invalid
/// - Required metadata fields are missing
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::parser::parse_markdown_file;
/// use std::path::Path;
///
/// let (metadata, content) = parse_markdown_file(Path::new("/tmp/test.md"))?;
/// println!("Title: {}", metadata.title);
/// println!("Category: {}", metadata.category);
/// println!("Content: {}", content);
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn parse_markdown_file(file_path: &Path) -> Result<(ItemMetadata, String)> {
    let content = fs::read_to_string(file_path)?;

    let matter = Matter::<YAML>::new();
    let result = matter.parse(&content);

    // Parse frontmatter into ItemMetadata
    // gray_matter returns Pod which can be deserialized directly
    let metadata: ItemMetadata = if let Some(data) = result.data {
        data.deserialize()
            .map_err(|e| anyhow::anyhow!("Failed to parse frontmatter: {}", e))?
    } else {
        return Err(anyhow::anyhow!("No frontmatter found in file"));
    };

    // Extract content body
    let body = result.content;

    Ok((metadata, body))
}

/// Validate frontmatter metadata
///
/// Checks that all required fields are present and non-empty.
/// Also validates RFC3339 timestamp format and category values.
///
/// Required fields: title, category, created, modified
///
/// # Arguments
///
/// * `metadata` - The metadata to validate
///
/// # Returns
///
/// `true` if metadata is valid, `false` otherwise
///
/// # Validation Rules
///
/// - `title` must be non-empty
/// - `category` must be non-empty and one of: Inbox, People, Projects, Ideas, Admin
/// - `created` must be non-empty and valid RFC3339 timestamp
/// - `modified` must be non-empty and valid RFC3339 timestamp
///
/// # Example
///
/// ```
/// use noosphere_sync::vault::template::ItemMetadata;
/// use noosphere_sync::vault::parser::validate_frontmatter;
/// use uuid::Uuid;
/// use chrono::Utc;
///
/// let metadata = ItemMetadata {
///     id: Uuid::new_v4(),
///     title: "Test".to_string(),
///     category: "Ideas".to_string(),
///     subcategory: None,
///     tags: vec![],
///     created: Utc::now().to_rfc3339(),
///     modified: Utc::now().to_rfc3339(),
///     state: "active".to_string(),
///     confidence: None,
/// };
///
/// assert!(validate_frontmatter(&metadata));
/// ```
pub fn validate_frontmatter(metadata: &ItemMetadata) -> bool {
    // Check required fields are non-empty
    if metadata.title.is_empty()
        || metadata.category.is_empty()
        || metadata.created.is_empty()
        || metadata.modified.is_empty()
    {
        return false;
    }

    // Validate RFC3339 timestamps
    if chrono::DateTime::parse_from_rfc3339(&metadata.created).is_err() {
        return false;
    }
    if chrono::DateTime::parse_from_rfc3339(&metadata.modified).is_err() {
        return false;
    }

    // Validate category is one of the allowed values
    const ALLOWED_CATEGORIES: &[&str] = &["Inbox", "People", "Projects", "Ideas", "Admin"];
    if !ALLOWED_CATEGORIES.contains(&metadata.category.as_str()) {
        return false;
    }

    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use std::io::Write;
    use tempfile::NamedTempFile;
    use uuid::Uuid;

    #[test]
    fn test_parse_valid_markdown() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        let test_id = Uuid::new_v4();
        let now = Utc::now().to_rfc3339();

        let content = format!(
            r#"---
id: {}
title: Test Item
category: Ideas
subcategory: Projects
tags:
  - test
  - example
created: {}
modified: {}
state: active
confidence: 0.95
---

# Test Item

This is the content body.
"#,
            test_id, now, now
        );

        write!(temp_file, "{}", content)?;
        temp_file.flush()?;

        let (metadata, body) = parse_markdown_file(temp_file.path())?;

        assert_eq!(metadata.title, "Test Item");
        assert_eq!(metadata.category, "Ideas");
        assert_eq!(metadata.subcategory, Some("Projects".to_string()));
        assert_eq!(metadata.tags, vec!["test", "example"]);
        assert_eq!(metadata.state, "active");
        assert_eq!(metadata.confidence, Some(0.95));
        assert!(body.contains("This is the content body"));

        Ok(())
    }

    #[test]
    fn test_parse_minimal_frontmatter() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        let test_id = Uuid::new_v4();
        let now = Utc::now().to_rfc3339();

        let content = format!(
            r#"---
id: {}
title: Minimal
category: Inbox
subcategory: null
tags: []
created: {}
modified: {}
state: uncategorized
confidence: null
---

Content here.
"#,
            test_id, now, now
        );

        write!(temp_file, "{}", content)?;
        temp_file.flush()?;

        let (metadata, body) = parse_markdown_file(temp_file.path())?;

        assert_eq!(metadata.title, "Minimal");
        assert_eq!(metadata.category, "Inbox");
        assert_eq!(metadata.subcategory, None);
        assert_eq!(metadata.tags.len(), 0);
        assert_eq!(metadata.confidence, None);
        assert!(body.contains("Content here"));

        Ok(())
    }

    #[test]
    fn test_parse_invalid_yaml() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;

        let content = r#"---
invalid yaml: [unclosed bracket
title: Test
---

Content
"#;

        write!(temp_file, "{}", content)?;
        temp_file.flush()?;

        let result = parse_markdown_file(temp_file.path());
        assert!(result.is_err());

        Ok(())
    }

    #[test]
    fn test_parse_missing_frontmatter() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;

        let content = r#"# Just a heading

No frontmatter here.
"#;

        write!(temp_file, "{}", content)?;
        temp_file.flush()?;

        let result = parse_markdown_file(temp_file.path());
        // Should fail because no frontmatter
        assert!(result.is_err());

        Ok(())
    }

    #[test]
    fn test_validate_frontmatter_valid() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Valid".to_string(),
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: None,
        };

        assert!(validate_frontmatter(&metadata));
    }

    #[test]
    fn test_validate_frontmatter_missing_title() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "".to_string(), // Empty title
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: None,
        };

        assert!(!validate_frontmatter(&metadata));
    }

    #[test]
    fn test_validate_frontmatter_missing_category() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test".to_string(),
            category: "".to_string(), // Empty category
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: None,
        };

        assert!(!validate_frontmatter(&metadata));
    }

    #[test]
    fn test_validate_frontmatter_invalid_timestamp() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test".to_string(),
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec![],
            created: "not-a-valid-timestamp".to_string(), // Invalid RFC3339
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: None,
        };

        assert!(!validate_frontmatter(&metadata));
    }

    #[test]
    fn test_validate_frontmatter_invalid_category() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test".to_string(),
            category: "InvalidCategory".to_string(), // Not in allowed list
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: None,
        };

        assert!(!validate_frontmatter(&metadata));
    }

    #[test]
    fn test_validate_frontmatter_missing_modified() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test".to_string(),
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: "".to_string(), // Empty modified
            state: "active".to_string(),
            confidence: None,
        };

        assert!(!validate_frontmatter(&metadata));
    }

    #[test]
    fn test_parse_unicode_content() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        let test_id = Uuid::new_v4();
        let now = Utc::now().to_rfc3339();

        let content = format!(
            r#"---
id: {}
title: Unicode Test 世界
category: Ideas
subcategory: null
tags: []
created: {}
modified: {}
state: active
confidence: null
---

# Unicode Content

Hello, 世界! 🌍
"#,
            test_id, now, now
        );

        write!(temp_file, "{}", content)?;
        temp_file.flush()?;

        let (metadata, body) = parse_markdown_file(temp_file.path())?;

        assert_eq!(metadata.title, "Unicode Test 世界");
        assert!(body.contains("Hello, 世界! 🌍"));

        Ok(())
    }
}
