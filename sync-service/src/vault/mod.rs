// Vault module for markdown file operations
// Provides utilities for creating, parsing, and writing markdown files with YAML frontmatter

pub mod hash;
pub mod lock;
pub mod parser;
pub mod template;
pub mod writer;

// Re-export public API for convenient imports
pub use hash::{compute_content_hash, compute_file_hash, has_content_changed};
pub use lock::FileLock;
pub use parser::{parse_markdown_file, validate_frontmatter};
pub use template::{create_item_template, ItemMetadata};
pub use writer::{update_frontmatter, write_markdown_file};
