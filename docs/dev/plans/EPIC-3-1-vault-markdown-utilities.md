# EPIC-3-1: Vault Directory Structure and Markdown Utilities

## Issue Reference
- **GitHub Issue**: #12
- **Epic**: File Vault System
- **Priority**: P1 (Core foundation)
- **Story Points**: 8
- **Service**: sync-service (Rust)

## Feature Summary

Implement a file-based knowledge vault with markdown utilities to enable markdown-based knowledge storage compatible with external tools like Obsidian and VSCode. **All vault filesystem operations are implemented in Rust (sync-service)**, NOT Python.

**Architecture Principle**: The local vault at `~/noosphere-vault/` is ONLY touched by Rust services (sync-service and cli). The Python api-service is stateless and never accesses the filesystem directly.

## Existing Codebase Analysis

**Current State**:
- ✅ sync-service/ directory exists
- ✅ Cargo.toml with basic dependencies (tokio, reqwest, serde, serde_yaml, sha2, anyhow, thiserror, tracing)
- ✅ src/main.rs (minimal scaffolding)
- ✅ tests/ directory (empty)

**Dependencies Already Present**:
- serde, serde_yaml, sha2, anyhow, thiserror ✓

**Dependencies to Add**:
- gray_matter (YAML frontmatter parsing)
- fs2 (file locking)
- uuid (UUID generation)
- chrono (timestamps)
- tempfile (atomic writes)

## Implementation Plan

### Files to Create

#### Module Files (sync-service/src/vault/):
1. **mod.rs** - Module exports and public API
2. **template.rs** - ItemMetadata struct + template generation
3. **parser.rs** - Markdown + frontmatter parsing (gray_matter)
4. **writer.rs** - Atomic file writing (tempfile)
5. **hash.rs** - SHA-256 content hashing
6. **lock.rs** - File locking with RAII (fs2)

#### Test Files (sync-service/tests/vault/):
7. **test_template.rs** - Template generation tests (3+ tests)
8. **test_parser.rs** - Parsing tests (4+ tests)
9. **test_writer.rs** - Writer tests (4+ tests)
10. **test_hash.rs** - Hash tests (3+ tests)
11. **test_lock.rs** - Lock tests (4+ tests)

#### Documentation:
12. **docs/vault-structure.md** - Vault structure documentation

### Files to Modify

1. **sync-service/Cargo.toml** - Add new dependencies

## Implementation Steps (In Order)

### 1. Update Dependencies (Cargo.toml)

Add to `[dependencies]` section:

```toml
# YAML frontmatter parsing
gray_matter = "0.2"

# File locking
fs2 = "0.4"

# UUID generation
uuid = { version = "1.0", features = ["v4", "serde"] }

# Timestamps
chrono = { version = "0.4", features = ["serde"] }

# Temporary files
tempfile = "3.0"
```

### 2. Create Module Structure (vault/mod.rs)

```rust
pub mod template;
pub mod parser;
pub mod writer;
pub mod hash;
pub mod lock;

// Re-export public API
pub use template::{ItemMetadata, create_item_template};
pub use parser::{parse_markdown_file, validate_frontmatter};
pub use writer::{write_markdown_file, update_frontmatter};
pub use hash::{compute_content_hash, compute_file_hash, has_content_changed};
pub use lock::FileLock;
```

### 3. Implement template.rs

**ItemMetadata struct** (authoritative schema from issue):

```rust
use serde::{Deserialize, Serialize};
use chrono::Utc;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ItemMetadata {
    pub id: Uuid,
    pub title: String,
    pub category: String,
    pub subcategory: Option<String>,
    pub tags: Vec<String>,
    pub created: String,          // RFC3339 timestamp
    pub modified: String,          // RFC3339 timestamp
    pub state: String,             // "uncategorized", etc.
    pub confidence: Option<f64>,   // AI classification confidence (0.0-1.0)
}

pub fn create_item_template(
    title: &str,
    category: &str,
    subcategory: Option<&str>,
    tags: Vec<String>,
    confidence: Option<f64>,
) -> String {
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

    let yaml = serde_yaml::to_string(&metadata).unwrap();
    format!("---\n{}---\n\n# {}\n\n[Content goes here...]\n", yaml, title)
}
```

### 4. Implement hash.rs

SHA-256 content hashing for change detection:

```rust
use sha2::{Sha256, Digest};
use std::fs;
use std::path::Path;
use anyhow::Result;

pub fn compute_content_hash(content: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(content.as_bytes());
    format!("{:x}", hasher.finalize())
}

pub fn compute_file_hash(file_path: &Path) -> Result<String> {
    let content = fs::read(file_path)?;
    let mut hasher = Sha256::new();
    hasher.update(&content);
    Ok(format!("{:x}", hasher.finalize()))
}

pub fn has_content_changed(file_path: &Path, cached_hash: Option<&str>) -> Result<bool> {
    let current_hash = compute_file_hash(file_path)?;

    match cached_hash {
        Some(cached) => Ok(current_hash != cached),
        None => Ok(true), // No cached hash, assume changed
    }
}
```

**Purpose**: Detect external file modifications (Obsidian edits), sync conflict detection, verify file integrity.

### 5. Implement lock.rs

File locking with RAII pattern (automatic cleanup):

```rust
use fs2::FileExt;
use std::fs::{self, File, OpenOptions};
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};
use anyhow::Result;

pub struct FileLock {
    lock_file: PathBuf,
    _guard: Option<File>,
}

impl FileLock {
    pub fn new(file_path: &Path) -> Self {
        let lock_dir = file_path
            .parent()
            .unwrap()
            .join(".noosphere/locks");
        fs::create_dir_all(&lock_dir).ok();

        let lock_file = lock_dir.join(format!(
            "{}.lock",
            file_path.file_name().unwrap().to_string_lossy()
        ));

        Self {
            lock_file,
            _guard: None,
        }
    }

    pub fn acquire(&mut self, timeout: Duration) -> Result<()> {
        let start = SystemTime::now();

        loop {
            match OpenOptions::new()
                .write(true)
                .create(true)
                .open(&self.lock_file)
            {
                Ok(file) => {
                    // Acquire exclusive lock
                    file.lock_exclusive()?;
                    self._guard = Some(file);
                    return Ok(());
                }
                Err(e) => {
                    if start.elapsed()? > timeout {
                        anyhow::bail!("Lock timeout");
                    }
                    std::thread::sleep(Duration::from_millis(100));
                }
            }
        }
    }

    pub fn release(&mut self) -> Result<()> {
        if let Some(file) = &self._guard {
            file.unlock()?;
        }
        self._guard = None;
        fs::remove_file(&self.lock_file).ok();
        Ok(())
    }
}

impl Drop for FileLock {
    fn drop(&mut self) {
        let _ = self.release();
    }
}
```

**Lock Strategy**: Advisory locks visible to both sync-service and cli, timeout mechanism prevents deadlocks, RAII auto-cleanup on drop.

### 6. Implement parser.rs

Markdown + frontmatter parsing using gray_matter:

```rust
use gray_matter::{engine::YAML, Matter};
use std::fs;
use std::path::Path;
use anyhow::Result;
use crate::vault::template::ItemMetadata;

pub fn parse_markdown_file(file_path: &Path) -> Result<(ItemMetadata, String)> {
    let content = fs::read_to_string(file_path)?;

    let matter = Matter::<YAML>::new();
    let result = matter.parse(&content);

    // Parse frontmatter into ItemMetadata
    let metadata: ItemMetadata = serde_yaml::from_str(&result.data.unwrap_or_default())?;

    // Extract content body
    let body = result.content;

    Ok((metadata, body))
}

pub fn validate_frontmatter(metadata: &ItemMetadata) -> bool {
    // Validate required fields are present
    !metadata.title.is_empty()
        && !metadata.category.is_empty()
        && !metadata.created.is_empty()
}
```

**Compatibility**: Uses standard YAML frontmatter format compatible with Obsidian, VSCode, Jekyll, Hugo.

### 7. Implement writer.rs

Atomic file writing with tempfile:

```rust
use std::fs;
use std::path::Path;
use anyhow::Result;
use tempfile::NamedTempFile;
use std::io::Write;
use crate::vault::template::ItemMetadata;
use crate::vault::parser::parse_markdown_file;

pub fn write_markdown_file(
    file_path: &Path,
    metadata: &ItemMetadata,
    content: &str,
) -> Result<()> {
    // Serialize metadata to YAML
    let yaml = serde_yaml::to_string(metadata)?;

    // Combine frontmatter + content
    let markdown = format!("---\n{}---\n\n{}", yaml, content);

    // Atomic write: temp file + rename
    atomic_write(file_path, &markdown)?;

    Ok(())
}

fn atomic_write(file_path: &Path, content: &str) -> Result<()> {
    // Create parent directory if needed
    if let Some(parent) = file_path.parent() {
        fs::create_dir_all(parent)?;
    }

    // Write to temp file in same directory
    let dir = file_path.parent().unwrap_or_else(|| Path::new("."));
    let mut temp_file = NamedTempFile::new_in(dir)?;
    temp_file.write_all(content.as_bytes())?;
    temp_file.flush()?;

    // Atomic rename (POSIX guarantee)
    temp_file.persist(file_path)?;

    Ok(())
}

pub fn update_frontmatter(
    file_path: &Path,
    updates: impl Fn(&mut ItemMetadata),
) -> Result<()> {
    // Read existing file
    let (mut metadata, content) = parse_markdown_file(file_path)?;

    // Apply updates
    updates(&mut metadata);

    // Write back
    write_markdown_file(file_path, &metadata, &content)?;

    Ok(())
}
```

**Atomic Operations**: Write to temp file in same directory, then atomic rename via `persist()`. Prevents partial writes and race conditions.

### 8. Create Documentation (docs/vault-structure.md)

Document:
- Vault directory structure (`~/noosphere-vault/`)
- Category folders (Inbox, People, Projects, Ideas, Admin)
- Subcategory creation guidelines
- File naming conventions (sanitization, special characters)
- Frontmatter metadata specification (required vs optional fields)
- External tool compatibility (Obsidian, VSCode)
- Examples of valid markdown files

### 9. Write Comprehensive Tests

#### test_template.rs (3 tests)
- `test_create_template` - Generates valid YAML frontmatter
- `test_template_fields` - All fields present and correct types
- `test_template_optional_fields` - Handle None/Some for optional fields

#### test_parser.rs (4 tests)
- `test_parse_valid_markdown` - Happy path parsing
- `test_parse_invalid_yaml` - Malformed frontmatter error handling
- `test_parse_missing_frontmatter` - Missing --- delimiters
- `test_validate_frontmatter` - Required fields validation

#### test_writer.rs (4 tests)
- `test_write_markdown_file` - Create new file with frontmatter
- `test_update_frontmatter` - Update metadata without changing content
- `test_atomic_write` - Verify atomicity (temp file + rename)
- `test_writer_creates_parent_dirs` - Auto-create directories

#### test_hash.rs (3 tests)
- `test_compute_content_hash` - SHA-256 computation correctness
- `test_hash_deterministic` - Same input produces same hash
- `test_has_content_changed` - Detect content changes correctly

#### test_lock.rs (4 tests)
- `test_file_lock_acquire_release` - Basic lock/unlock
- `test_lock_timeout` - Timeout behavior when lock held
- `test_lock_auto_cleanup` - RAII Drop trait cleanup
- `test_concurrent_locks` - Multiple process safety

**Total**: 18 tests minimum, **target 80%+ coverage**

## Architecture Decisions

### Design as Reusable Library
- Vault module is pure library code (no main.rs dependencies)
- Can be used by both sync-service and cli
- Well-documented public API
- Thoroughly tested
- Independent of service-specific logic

### Error Handling Strategy
- Use `anyhow::Result<T>` for function returns
- Use `thiserror` for custom error types (if needed later)
- Proper error propagation with context
- Informative error messages

### Atomic File Operations
- Use `tempfile::NamedTempFile::new_in(dir)` - temp file in same directory
- Write content to temp file
- Call `persist()` for atomic rename (POSIX guarantee)
- Prevents partial writes and race conditions
- Safe for concurrent operations

### File Locking
- Advisory locks using fs2 crate (cross-platform)
- Lock files stored in `.noosphere/locks/` directory
- Timeout mechanism (prevents deadlocks)
- RAII pattern (automatic cleanup on drop)
- Visible to both sync-service and cli
- Stale lock detection (future enhancement)

### Obsidian Compatibility
- Standard YAML frontmatter format
- Compatible with Obsidian, VSCode, Jekyll, Hugo
- No custom extensions that break compatibility
- Metadata fields don't conflict with Obsidian reserved fields
- Content can include Obsidian markdown (wikilinks, tags)

## Testing Strategy

**Coverage Target**: 80%+ minimum

**Test Categories**:
- ✅ Happy path (valid inputs, expected outputs)
- ✅ Error cases (missing fields, invalid YAML, I/O errors)
- ✅ Edge cases (unicode, empty files, missing directories)
- ✅ Atomicity (concurrent operations, partial writes)
- ✅ Locking (timeouts, stale locks, cleanup)

**Test Tools**:
- `cargo test --package noosphere-sync --lib vault`
- `cargo-llvm-cov` for coverage reporting
- `tempfile` for temporary test directories

## Verification

### Quality Checks
```bash
cd sync-service

# Format code
cargo fmt

# Linting
cargo clippy --package noosphere-sync -- -D warnings

# Type checking (implicit in clippy)
cargo check --package noosphere-sync

# Run tests
cargo test --package noosphere-sync --lib vault

# Coverage report
cargo llvm-cov --package noosphere-sync --lib vault --html
open target/llvm-cov/html/index.html
```

### Manual Verification
```bash
# Vault structure verification
ls -la ~/noosphere-vault/
# Should show: Inbox/, People/, Projects/, Ideas/, Admin/, .noosphere-metadata

# Template generation test
cd sync-service
cargo test --package noosphere-sync test_create_template -- --nocapture

# Parser test
cargo test --package noosphere-sync test_parse_markdown -- --nocapture

# Full test suite
cargo test --lib vault -- --nocapture

# Expected: 18+ tests passed, 0 failed
```

### Obsidian Compatibility Test
1. Generate test markdown file using template
2. Open in Obsidian
3. Verify frontmatter displays correctly
4. Edit in Obsidian
5. Parse with vault utilities
6. Verify changes detected

## Dependencies and Blockers

**Blocks**:
- EPIC-5-2 (sync-service will use vault utilities for file operations)

**Blocked By**:
- EPIC-2-2 (Item model defines metadata schema for REST API contract) - Schema defined in this issue

**Related**:
- EPIC-3-2 (File locking - implemented in lock.rs module)
- EPIC-4-1 (Configuration will specify vault path)

## Performance Considerations

- **Hash Computation**: Fast (~1ms for typical note)
- **Cache Hashes**: Store in memory to avoid recomputation
- **Only Recompute**: When file modified timestamp changes
- **Async I/O**: Future enhancement for sync-service integration
- **Batch Operations**: Future enhancement for multiple files

## Completion Criteria

- [x] All dependencies added to Cargo.toml
- [x] Module structure created (vault/mod.rs)
- [x] template.rs implemented (ItemMetadata + template generation)
- [x] hash.rs implemented (SHA-256 hashing)
- [x] lock.rs implemented (file locking with RAII)
- [x] parser.rs implemented (frontmatter parsing)
- [x] writer.rs implemented (atomic file writes)
- [x] Documentation created (docs/vault-structure.md)
- [x] All tests written (18+ tests)
- [x] All tests pass
- [x] Coverage >= 80%
- [x] Clippy passes with no warnings
- [x] Can create, read, and update markdown files programmatically
- [x] Files are compatible with Obsidian (manual verification)
