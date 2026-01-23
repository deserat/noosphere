# Vault Structure Documentation

## Overview

The Noosphere vault is a file-based knowledge management system stored at `~/noosphere-vault/`. It uses markdown files with YAML frontmatter, making it compatible with external tools like Obsidian, VSCode, and other markdown editors.

**Key Principles**:
- ✅ All vault files are managed by **Rust services only** (sync-service and cli)
- ✅ Python api-service **never** touches the vault filesystem
- ✅ Standard YAML frontmatter format (compatible with Obsidian, Jekyll, Hugo)
- ✅ Human-readable and editable in any text editor

## Directory Structure

```
~/noosphere-vault/
├── Inbox/              # Uncategorized items awaiting triage
├── People/             # Notes about individuals
├── Projects/           # Active and archived projects
├── Ideas/              # Creative and philosophical ideas
├── Admin/              # Tasks, meeting notes, administrative items
├── .noosphere/         # Metadata directory (auto-managed)
│   ├── locks/          # File locks for concurrent access
│   └── cache/          # Content hashes (future)
└── .noosphere-metadata # Vault configuration (YAML)
```

### Category Folders

| Category | Purpose | Examples |
|----------|---------|----------|
| **Inbox** | Uncategorized items awaiting triage | Quick captures, unsorted notes |
| **People** | Notes about individuals | Contact info, meeting notes, relationships |
| **Projects** | Active and archived projects | Project plans, documentation, progress tracking |
| **Ideas** | Creative and philosophical ideas | Brainstorms, concepts, inspirations |
| **Admin** | Tasks, meeting notes, administrative items | To-dos, agendas, administrative tasks |

### Subcategory Creation Guidelines

Subcategories are optional and created as subdirectories within category folders:

```
~/noosphere-vault/
├── Projects/
│   ├── Work/           # Work-related projects
│   ├── Personal/       # Personal projects
│   └── Archive/        # Archived projects
└── Ideas/
    ├── Technical/      # Technical ideas
    └── Creative/       # Creative ideas
```

**Best Practices**:
- Keep subcategory structure shallow (max 2 levels recommended)
- Use consistent naming (CamelCase or kebab-case)
- Avoid special characters in folder names
- Create subcategories as needed, don't over-architect

## File Naming Conventions

### Filename Format

Pattern: `{title-kebab-case}.md`

**Sanitization Rules**:
- Convert to lowercase
- Replace spaces with hyphens (`-`)
- Remove special characters (except hyphens)
- Limit to alphanumeric and hyphens

**Examples**:
- Title: "Build Automation Dashboard" → Filename: `build-automation-dashboard.md`
- Title: "Meeting Notes: Q1 Planning" → Filename: `meeting-notes-q1-planning.md`
- Title: "User Story #42" → Filename: `user-story-42.md`

### Full Path Examples

```
~/noosphere-vault/Inbox/quick-capture-2024-01-15.md
~/noosphere-vault/People/john-doe.md
~/noosphere-vault/Projects/Work/api-redesign.md
~/noosphere-vault/Ideas/Technical/rust-microservices.md
~/noosphere-vault/Admin/weekly-review-2024-w03.md
```

## Frontmatter Metadata Specification

### Required Fields

All markdown files **must** include these fields in YAML frontmatter:

```yaml
---
id: 550e8400-e29b-41d4-a716-446655440000  # UUID (auto-generated)
title: Build Automation Dashboard            # Human-readable title
category: Ideas                              # Primary category
subcategory: Technical                       # Optional subcategory
tags: []                                     # List of tags
created: 2024-01-15T10:00:00Z               # ISO 8601 timestamp
modified: 2024-01-15T10:00:00Z              # ISO 8601 timestamp
state: uncategorized                         # Item state
confidence: null                             # AI confidence (0.0-1.0)
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✅ Yes | Unique identifier (auto-generated, never changes) |
| `title` | String | ✅ Yes | Human-readable title |
| `category` | String | ✅ Yes | Primary category (Inbox, People, Projects, Ideas, Admin) |
| `subcategory` | String | ❌ No | Optional subcategory for organization |
| `tags` | Array[String] | ✅ Yes | List of tags (can be empty) |
| `created` | String | ✅ Yes | Creation timestamp (RFC3339/ISO 8601) |
| `modified` | String | ✅ Yes | Last modification timestamp (RFC3339/ISO 8601) |
| `state` | String | ✅ Yes | Item state (uncategorized, active, archived) |
| `confidence` | Float | ❌ No | AI classification confidence (0.0 to 1.0) |

### Field Validation Rules

**title**:
- Must not be empty
- Should be concise and descriptive
- Can contain any Unicode characters

**category**:
- Must not be empty
- Must be one of: Inbox, People, Projects, Ideas, Admin
- Case-sensitive

**tags**:
- Array of strings
- Can be empty (`[]`)
- Each tag should be lowercase
- Use hyphens for multi-word tags (`project-planning`)

**created / modified**:
- RFC3339 format: `2024-01-15T10:00:00Z`
- Must include timezone (typically UTC with `Z` suffix)
- `modified` updated on every change

**state**:
- Common values: `uncategorized`, `active`, `archived`, `completed`
- Can be custom values as needed

**confidence**:
- Optional (can be `null`)
- Float between 0.0 and 1.0
- Represents AI classification confidence

## Complete File Example

```markdown
---
id: 550e8400-e29b-41d4-a716-446655440000
title: Build Home Automation Dashboard
category: Ideas
subcategory: Technical
tags:
  - automation
  - smart-home
  - dashboard
created: 2024-01-15T10:00:00Z
modified: 2024-01-15T14:30:00Z
state: active
confidence: 0.95
---

# Build Home Automation Dashboard

Need to build a centralized dashboard for controlling all smart home devices.
Should integrate with Home Assistant and provide:

## Requirements

- Real-time device status monitoring
- Automation rule editor (visual interface)
- Energy usage monitoring with graphs
- Voice control integration (Alexa/Google)

## Technical Stack

Considering:
- Frontend: React + TypeScript
- Backend: Rust (for performance)
- Database: PostgreSQL
- Real-time: WebSockets

## Next Steps

1. Research existing dashboards (Home Assistant, openHAB)
2. Design UI mockups in Figma
3. Prototype basic device control
4. Implement automation editor

## References

- [[Home Assistant Integration]]
- [[Smart Home Architecture]]
```

## External Tool Compatibility

### Obsidian Compatibility

The vault is **fully compatible** with Obsidian:

✅ **Supported Features**:
- YAML frontmatter (displays in metadata panel)
- Markdown content with all Obsidian syntax
- Wikilinks: `[[Note Title]]`
- Tags in frontmatter
- Backlinks and graph view
- External editing detection (auto-reloads)

⚠️ **Considerations**:
- Avoid Obsidian-specific frontmatter fields (`aliases`, `cssclass`, etc.)
- Our custom fields (`confidence`, `state`) are ignored by Obsidian (harmless)
- File moves in Obsidian don't update our `category` field (manual sync needed)

**Workflow**:
1. Edit files in Obsidian normally
2. sync-service detects changes and syncs to database
3. AI classification updates frontmatter
4. Obsidian auto-reloads with new metadata

### VSCode Compatibility

Works with VSCode + markdown extensions:

✅ **Recommended Extensions**:
- Markdown All in One
- Markdown Preview Enhanced
- YAML (for frontmatter syntax highlighting)

✅ **Features**:
- Syntax highlighting for frontmatter
- Live markdown preview
- File navigation
- Search across vault

### Other Compatible Tools

- **Jekyll / Hugo**: Uses same frontmatter format
- **Foam**: VSCode-based knowledge management
- **Zettlr**: Academic writing tool
- **Typora**: WYSIWYG markdown editor
- **Any text editor**: Files are plain text

## Vault Initialization

The vault is automatically initialized on first run of sync-service:

```bash
# Created by sync-service on first run
~/noosphere-vault/
├── Inbox/              # Empty directory
├── People/             # Empty directory
├── Projects/           # Empty directory
├── Ideas/              # Empty directory
├── Admin/              # Empty directory
└── .noosphere-metadata # Configuration file
```

### .noosphere-metadata File

```yaml
vault_version: "1.0"
created: "2024-01-15T12:00:00Z"
categories:
  - Inbox
  - People
  - Projects
  - Ideas
  - Admin
```

## File Operations

### Creating Files

**Option 1**: Via cli (recommended)
```bash
noosphere-cli create --title "My Idea" --category Ideas
# Creates: ~/noosphere-vault/Ideas/my-idea.md
```

**Option 2**: Manually (advanced)
1. Create file in appropriate category folder
2. Add frontmatter with all required fields
3. sync-service detects and syncs to database

**Option 3**: Via Obsidian
1. Create note normally in Obsidian
2. Add our required frontmatter fields
3. sync-service syncs to database

### Editing Files

**Recommended**: Edit in Obsidian or VSCode
- Changes detected automatically
- Frontmatter preserved
- Content synced to database

**Programmatic**: Use vault utilities
```rust
use noosphere_sync::vault::writer::update_frontmatter;
use std::path::Path;
use chrono::Utc;

let file_path = Path::new("/home/user/noosphere-vault/Ideas/my-note.md");

// Update the category and modified timestamp
update_frontmatter(file_path, |meta| {
    meta.category = "Projects".to_string();
    meta.modified = Utc::now().to_rfc3339();
})?;
```

### Moving Files

⚠️ **Warning**: Moving files between folders requires updating frontmatter.

**Correct Process**:
1. Update `category` (and `subcategory` if needed) in frontmatter
2. Then move file to matching folder
3. sync-service syncs updated metadata

**Example**:
```rust
use std::path::Path;
use std::fs;
use noosphere_sync::vault::writer::update_frontmatter;

// Define vault base path (typically obtained from config)
let vault_path = Path::new("/home/user/noosphere-vault");

// Construct paths relative to vault base
let old_path = vault_path.join("Ideas/project.md");
let new_path = vault_path.join("Projects/Work/project.md");

// 1. Update frontmatter before moving
update_frontmatter(&old_path, |metadata| {
    metadata.category = "Projects".to_string();
    metadata.subcategory = Some("Work".to_string());
})?;

// 2. Ensure destination directory exists
if let Some(parent) = new_path.parent() {
    fs::create_dir_all(parent)?;
}

// 3. Move file atomically
fs::rename(&old_path, &new_path)?;
```

**Note**: The `~` character is expanded by shells but not by Rust's standard library.
Always use absolute paths or construct paths from a base directory variable.

### Deleting Files

**Option 1**: Via cli
```bash
noosphere-cli delete <item-id>
# Deletes both file and database record
```

**Option 2**: Manually
1. Delete file from vault
2. sync-service detects deletion
3. Database record marked as deleted

## Concurrent Access

### File Locking

sync-service and cli use file locks to prevent concurrent writes:

```
~/noosphere-vault/Ideas/.noosphere/locks/my-idea.md.lock
```

**Lock Behavior**:
- Advisory locks (visible to both sync-service and cli)
- Timeout after 5 seconds (prevents deadlocks)
- Auto-cleanup on process exit (RAII pattern)
- Not visible to Obsidian (potential conflict)

### Conflict Resolution

**Strategy**: Last-write-wins

1. Both sync-service and Obsidian edit same file
2. sync-service detects change via content hash
3. Later write overwrites earlier write
4. Warning logged for user

**Best Practice**: Don't edit same file simultaneously in multiple tools.

## Content Hashing

sync-service computes SHA-256 hashes to detect external modifications:

**Purpose**:
- Detect Obsidian edits
- Verify file integrity
- Sync conflict detection
- Avoid redundant syncs

**Performance**:
- Hash computation: ~1ms per note
- Hashes cached in memory
- Only recompute when file mtime changes

## Metadata Directory

`.noosphere/` directory (auto-managed, don't edit):

```
~/noosphere-vault/.noosphere/
├── locks/              # File locks (*.lock files)
└── cache/              # Future: Content hash cache
```

**Git Ignore**: Add to `.gitignore` if vault is version-controlled:
```
.noosphere/
```

## Best Practices

### Organizing Content

1. **Start in Inbox**: Capture everything to Inbox initially
2. **Triage Regularly**: Move items to appropriate categories
3. **Use Subcategories Sparingly**: Only when needed for organization
4. **Tag Liberally**: Tags are flexible, folders are rigid
5. **Link Generously**: Use `[[wikilinks]]` to connect related notes

### Frontmatter Hygiene

1. **Don't Edit id/created**: These should never change
2. **Update modified**: Auto-updated by sync-service
3. **Use Consistent Tags**: Lowercase, hyphens for multi-word
4. **Meaningful Titles**: Descriptive, unique, searchable
5. **Proper Categories**: Use the 5 defined categories

### External Editing

1. **Obsidian**: Preferred for daily use
2. **VSCode**: Good for batch operations
3. **cli**: For automation and scripting
4. **Avoid Simultaneous Edits**: One tool at a time per file

## Troubleshooting

### File Not Syncing

**Symptoms**: File created but not in database

**Solutions**:
1. Check frontmatter is valid YAML
2. Verify all required fields present
3. Check sync-service logs
4. Manually trigger sync (restart sync-service)

### Invalid Frontmatter

**Symptoms**: Parsing errors in logs

**Solutions**:
1. Validate YAML syntax (use YAML linter)
2. Check field types (UUID, timestamps, etc.)
3. Ensure no tabs in YAML (use spaces)
4. Check for special characters in values

### Lock Timeout

**Symptoms**: "Lock timeout" error

**Solutions**:
1. Check for stale lock files in `.noosphere/locks/`
2. Ensure no hung processes
3. Increase timeout (rare)
4. Manually remove lock file (last resort)

### Obsidian Not Reloading

**Symptoms**: Frontmatter changes not visible in Obsidian

**Solutions**:
1. Close and reopen file in Obsidian
2. Restart Obsidian
3. Check Obsidian auto-reload settings
4. Verify file saved correctly

## Future Enhancements

Planned features for later phases:

- **Additional Fields**: `surfaced`, `next_surface`, `cadence` (resurfacing)
- **Hash Cache**: Persistent cache for faster change detection
- **Stale Lock Detection**: Auto-cleanup of abandoned locks
- **Backup/Restore**: Automated vault backups
- **Sync Conflicts UI**: Visual conflict resolution
- **Batch Operations**: Bulk file updates via cli

## References

- [Obsidian Documentation](https://help.obsidian.md/)
- [YAML Specification](https://yaml.org/spec/1.2.2/)
- [Markdown Guide](https://www.markdownguide.org/)
- [RFC3339 Timestamps](https://www.rfc-editor.org/rfc/rfc3339)
