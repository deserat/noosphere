# Vault Directory Structure and Markdown Utilities

**Epic**: File Vault System
**Priority**: P1
**Story Points**: 8

## User Story

Implement a file-based knowledge vault with markdown utilities to enable markdown-based knowledge storage compatible with external tools like Obsidian and VSCode.

## Acceptance Criteria

### Vault Directory Structure
- [ ] Vault directory created at `~/noosphere-vault/`:
  ```bash
  mkdir -p ~/noosphere-vault
  ```
- [ ] Category folders created:
  - `Inbox/` - Uncategorized items awaiting triage
  - `People/` - Notes about individuals
  - `Projects/` - Active and archived projects
  - `Ideas/` - Creative and philosophical ideas
  - `Admin/` - Tasks, meeting notes, administrative items
- [ ] `.noosphere-metadata` file created with vault configuration:
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
- [ ] Vault structure documented in `docs/vault-structure.md`:
  - Purpose of each category
  - Subcategory creation guidelines
  - File naming conventions
  - Frontmatter metadata specification
  - External tool compatibility notes (Obsidian, VSCode, etc.)

### Markdown Template Module
- [ ] `api-service/app/vault/template.py` created with frontmatter template function:
  ```python
  from datetime import datetime
  import uuid

  def create_item_template(
      title: str,
      category: str,
      subcategory: str | None = None,
      tags: list[str] = None,
      confidence: float | None = None
  ) -> str:
      """Generate markdown template with frontmatter."""
      frontmatter = f"""---
  id: {uuid.uuid4()}
  title: \"{title}\"
  category: {category}
  subcategory: {subcategory or ''}
  tags: {tags or []}
  created: {datetime.utcnow().isoformat()}Z
  modified: {datetime.utcnow().isoformat()}Z
  state: uncategorized
  confidence: {confidence or 0.0}
  ---

  # {title}

  [Content goes here...]
  """
      return frontmatter
  ```
- [ ] Template includes all required frontmatter fields:
  - Identity: id, title
  - Classification: category, subcategory, tags
  - Timestamps: created, modified, last_worked, categorized_at
  - State: state, next_surface, cadence
  - AI: confidence, embedding_updated
  - Privacy: no_ai
  - Sync: content_hash

### Markdown Parser Module
- [ ] `api-service/app/vault/parser.py` created for parsing markdown + frontmatter:
  ```python
  import frontmatter
  from typing import Dict, Any

  def parse_markdown_file(file_path: str) -> Dict[str, Any]:
      """Parse markdown file and extract frontmatter + content."""
      with open(file_path, 'r', encoding='utf-8') as f:
          post = frontmatter.load(f)

      return {
          'metadata': dict(post.metadata),
          'content': post.content
      }

  def validate_frontmatter(metadata: Dict[str, Any]) -> bool:
      """Validate frontmatter has required fields."""
      required = ['id', 'title', 'category', 'created', 'state']
      return all(field in metadata for field in required)
  ```
- [ ] Parser handles:
  - YAML frontmatter extraction
  - Content body extraction
  - Metadata validation
  - Error handling for malformed files
  - Unicode/UTF-8 support

### Markdown Writer Module
- [ ] `api-service/app/vault/writer.py` created for writing markdown with frontmatter:
  ```python
  import frontmatter
  from pathlib import Path

  def write_markdown_file(
      file_path: str,
      metadata: Dict[str, Any],
      content: str
  ) -> None:
      """Write markdown file with frontmatter."""
      post = frontmatter.Post(content, **metadata)

      # Ensure directory exists
      Path(file_path).parent.mkdir(parents=True, exist_ok=True)

      with open(file_path, 'w', encoding='utf-8') as f:
          f.write(frontmatter.dumps(post))

  def update_frontmatter(
      file_path: str,
      updates: Dict[str, Any]
  ) -> None:
      """Update frontmatter fields without changing content."""
      data = parse_markdown_file(file_path)
      data['metadata'].update(updates)
      write_markdown_file(file_path, data['metadata'], data['content'])
  ```
- [ ] Writer handles:
  - Atomic file writes (write to temp, then rename)
  - Directory creation
  - Metadata updates
  - UTF-8 encoding

### Content Hash Implementation
- [ ] Content hash computation (SHA-256):
  ```python
  import hashlib

  def compute_content_hash(content: str) -> str:
      """Compute SHA-256 hash of content for sync conflict detection."""
      return hashlib.sha256(content.encode('utf-8')).hexdigest()
  ```
- [ ] Hash includes both frontmatter and content:
  ```python
  def compute_file_hash(file_path: str) -> str:
      """Compute hash of entire file for sync."""
      with open(file_path, 'rb') as f:
          file_content = f.read()
      return hashlib.sha256(file_content).hexdigest()
  ```

### Unit Tests
- [ ] Test suite created in `api-service/tests/vault/`:
  - `test_template.py` - Template generation tests
  - `test_parser.py` - Parsing tests (valid/invalid frontmatter)
  - `test_writer.py` - Writing tests (file creation, updates)
  - `test_content_hash.py` - Hash computation tests
- [ ] Tests cover:
  - Happy path (valid inputs)
  - Error cases (missing fields, invalid YAML)
  - Unicode handling
  - File system edge cases (missing directories, permissions)
- [ ] All tests pass:
  ```bash
  pytest api-service/tests/vault/ -v
  ```

## Technical Notes

**Frontmatter Library**:
- Use `python-frontmatter` library for parsing/writing
- Handles YAML, TOML, JSON frontmatter formats
- Compatible with Obsidian, Jekyll, Hugo, etc.

**File Path Construction**:
- Pattern: `{category}/{subcategory}/{filename}.md`
- Example: `Ideas/Creative/blog-post-second-brain.md`
- Filename sanitization needed (remove special characters, spaces → hyphens)

**Atomic File Operations**:
```python
import tempfile
import os

def atomic_write(file_path: str, content: str) -> None:
    """Write file atomically to prevent partial writes."""
    dir_path = os.path.dirname(file_path)
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=dir_path,
        delete=False,
        encoding='utf-8'
    ) as temp_file:
        temp_file.write(content)
        temp_name = temp_file.name

    os.replace(temp_name, file_path)  # Atomic on POSIX
```

**Obsidian Compatibility**:
- Frontmatter format must be standard YAML
- Content can include Obsidian-specific markdown (wikilinks, etc.)
- Metadata fields should not conflict with Obsidian's reserved fields

**Content Hash Purpose**:
- Detect external file modifications (Obsidian edits)
- Sync conflict detection
- Verify file integrity
- Track changes for audit log

**Performance Considerations**:
- Hash computation is fast (~1ms for typical note)
- Cache hashes in database to avoid recomputation
- Only recompute when file modified timestamp changes

## Dependencies

- **Blocks**:
  - EPIC-5-1 (API service will use vault utilities for file operations)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed for src/vault directory)
  - EPIC-1-2 (Python environment needed for frontmatter library)
  - EPIC-2-2 (Item model defines metadata schema)
- **Related**:
  - EPIC-3-2 (File locking will use these utilities)
  - EPIC-4-1 (Configuration will specify vault path)

## Verification

### Vault Structure Verification
```bash
# Check vault directory exists
ls -la ~/noosphere-vault/
# Should show: Inbox/, People/, Projects/, Ideas/, Admin/, .noosphere-metadata

# Check metadata file
cat ~/noosphere-vault/.noosphere-metadata
# Should show valid YAML with categories listed

# Check each category folder
for category in Inbox People Projects Ideas Admin; do
  test -d ~/noosphere-vault/$category && echo "✓ $category exists"
done
```

### Template Module Test
```bash
cd api-service
source venv/bin/activate

python -c "
from app.vault.template import create_item_template

template = create_item_template(
    title='Test Item',
    category='Ideas',
    subcategory='Creative',
    tags=['test', 'example'],
    confidence=0.95
)

print(template)

# Verify frontmatter format
assert '---' in template
assert 'id:' in template
assert 'title: \"Test Item\"' in template
assert 'category: Ideas' in template
assert 'tags:' in template
print('✓ Template generation working')
"
```

### Parser Module Test
```bash
python -c "
from app.vault.parser import parse_markdown_file, validate_frontmatter
from app.vault.template import create_item_template
from app.vault.writer import write_markdown_file
import tempfile
import os

# Create test file
test_file = tempfile.mktemp(suffix='.md')
template = create_item_template('Parser Test', 'Ideas')
with open(test_file, 'w') as f:
    f.write(template)

# Parse file
data = parse_markdown_file(test_file)

assert 'metadata' in data
assert 'content' in data
assert data['metadata']['title'] == 'Parser Test'
assert validate_frontmatter(data['metadata'])

os.unlink(test_file)
print('✓ Parser working')
"
```

### Writer Module Test
```bash
python -c "
from app.vault.writer import write_markdown_file, update_frontmatter
from app.vault.parser import parse_markdown_file
import tempfile
import os

# Write new file
test_file = tempfile.mktemp(suffix='.md')
metadata = {
    'title': 'Writer Test',
    'category': 'Ideas',
    'state': 'not-started'
}
content = '# Writer Test\n\nThis is test content.'

write_markdown_file(test_file, metadata, content)

# Verify file exists
assert os.path.exists(test_file)

# Parse and verify
data = parse_markdown_file(test_file)
assert data['metadata']['title'] == 'Writer Test'
assert data['content'].strip() == content.strip()

# Update frontmatter
update_frontmatter(test_file, {'state': 'completed'})

# Verify update
data = parse_markdown_file(test_file)
assert data['metadata']['state'] == 'completed'

os.unlink(test_file)
print('✓ Writer working')
"
```

### Content Hash Test
```bash
python -c "
from app.vault.template import create_item_template
from app.vault.parser import compute_content_hash
import hashlib

content = 'Test content for hashing'
hash1 = compute_content_hash(content)

# Verify hash is SHA-256 (64 hex characters)
assert len(hash1) == 64

# Verify deterministic (same input = same hash)
hash2 = compute_content_hash(content)
assert hash1 == hash2

# Verify different content = different hash
hash3 = compute_content_hash('Different content')
assert hash1 != hash3

print(f'✓ Content hash working: {hash1[:16]}...')
"
```

### Unit Test Suite
```bash
cd api-service
pytest tests/vault/ -v

# Expected output:
# tests/vault/test_template.py::test_create_template PASSED
# tests/vault/test_template.py::test_template_fields PASSED
# tests/vault/test_parser.py::test_parse_valid PASSED
# tests/vault/test_parser.py::test_parse_invalid PASSED
# tests/vault/test_writer.py::test_write_file PASSED
# tests/vault/test_writer.py::test_update_frontmatter PASSED
# tests/vault/test_content_hash.py::test_hash_computation PASSED
# tests/vault/test_content_hash.py::test_hash_deterministic PASSED
#
# ======== 8 passed in 0.5s ========
```

**Completion Criteria**:
- [ ] Vault directory structure exists with all category folders
- [ ] Template module generates valid markdown with frontmatter
- [ ] Parser module extracts frontmatter and content correctly
- [ ] Writer module creates and updates files correctly
- [ ] Content hash computation works and is deterministic
- [ ] All unit tests pass
- [ ] Can create, read, and update markdown files programmatically
- [ ] Files are compatible with Obsidian (can open and edit)
- [ ] Documentation explains vault structure and file format
