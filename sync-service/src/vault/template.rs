// Template module for generating markdown files with YAML frontmatter

use anyhow::Result;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Item metadata stored in YAML frontmatter
///
/// This struct defines the authoritative schema for item metadata in Phase 1.
/// Additional fields (surfaced, next_surface, cadence) may be added in later phases.
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub struct ItemMetadata {
    /// Unique identifier for the item
    pub id: Uuid,

    /// Human-readable title
    pub title: String,

    /// Primary category (Inbox, People, Projects, Ideas, Admin)
    pub category: String,

    /// Optional subcategory for organization
    pub subcategory: Option<String>,

    /// Tags for additional classification
    pub tags: Vec<String>,

    /// Creation timestamp (RFC3339 format)
    pub created: String,

    /// Last modification timestamp (RFC3339 format)
    pub modified: String,

    /// Item state (uncategorized, active, archived, etc.)
    pub state: String,

    /// AI classification confidence score (0.0 to 1.0)
    pub confidence: Option<f64>,
}

/// Create a new markdown template with YAML frontmatter
///
/// Generates a complete markdown document with:
/// - YAML frontmatter containing item metadata
/// - Markdown heading with the title
/// - Placeholder for content
///
/// # Arguments
///
/// * `title` - The item title
/// * `category` - Primary category (Inbox, People, Projects, Ideas, Admin)
/// * `subcategory` - Optional subcategory for organization
/// * `tags` - List of tags for classification
/// * `confidence` - Optional AI classification confidence (0.0 to 1.0)
///
/// # Returns
///
/// A complete markdown string with YAML frontmatter
///
/// # Errors
///
/// Returns an error if metadata serialization to YAML fails
///
/// # Example
///
/// ```
/// use noosphere_sync::vault::template::create_item_template;
///
/// let markdown = create_item_template(
///     "Build automation dashboard",
///     "Ideas",
///     Some("Projects"),
///     vec!["automation".to_string(), "dashboard".to_string()],
///     Some(0.95),
/// )?;
///
/// assert!(markdown.contains("---"));
/// assert!(markdown.contains("title: Build automation dashboard"));
/// assert!(markdown.contains("category: Ideas"));
/// # Ok::<(), anyhow::Error>(())
/// ```
pub fn create_item_template(
    title: &str,
    category: &str,
    subcategory: Option<&str>,
    tags: Vec<String>,
    confidence: Option<f64>,
) -> Result<String> {
    let now = Utc::now().to_rfc3339();
    let metadata = ItemMetadata {
        id: Uuid::new_v4(),
        title: title.to_string(),
        category: category.to_string(),
        subcategory: subcategory.map(|s| s.to_string()),
        tags,
        created: now.clone(),
        modified: now,
        state: "uncategorized".to_string(),
        confidence,
    };

    let yaml = serde_yaml::to_string(&metadata)
        .map_err(|e| anyhow::anyhow!("Failed to serialize metadata: {}", e))?;
    Ok(format!(
        "---\n{}---\n\n# {}\n\n[Content goes here...]\n",
        yaml, title
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_template_basic() -> Result<()> {
        let template = create_item_template("Test Item", "Ideas", None, vec![], None)?;

        // Should have frontmatter delimiters
        assert!(template.starts_with("---\n"));
        assert!(template.contains("\n---\n"));

        // Should contain required fields
        assert!(template.contains("title: Test Item"));
        assert!(template.contains("category: Ideas"));
        assert!(template.contains("state: uncategorized"));

        // Should have markdown heading
        assert!(template.contains("# Test Item"));

        Ok(())
    }

    #[test]
    fn test_create_template_with_all_fields() -> Result<()> {
        let template = create_item_template(
            "Complete Item",
            "Projects",
            Some("Work"),
            vec!["urgent".to_string(), "backend".to_string()],
            Some(0.95),
        )?;

        assert!(template.contains("title: Complete Item"));
        assert!(template.contains("category: Projects"));
        assert!(template.contains("subcategory: Work"));
        assert!(template.contains("- urgent"));
        assert!(template.contains("- backend"));
        assert!(template.contains("confidence: 0.95"));

        Ok(())
    }

    #[test]
    fn test_metadata_struct() {
        let metadata = ItemMetadata {
            id: Uuid::new_v4(),
            title: "Test".to_string(),
            category: "Ideas".to_string(),
            subcategory: None,
            tags: vec![],
            created: Utc::now().to_rfc3339(),
            modified: Utc::now().to_rfc3339(),
            state: "active".to_string(),
            confidence: Some(0.8),
        };

        // Test serialization
        let yaml = serde_yaml::to_string(&metadata).unwrap();
        assert!(yaml.contains("title: Test"));

        // Test deserialization
        let deserialized: ItemMetadata = serde_yaml::from_str(&yaml).unwrap();
        assert_eq!(deserialized.title, "Test");
        assert_eq!(deserialized.category, "Ideas");
    }
}
