# Information Architecture

## File Structure

### Vault Organization (Category = Folder)

```
~/noosphere-vault/
  Inbox/              ← Uncategorized items (state: uncategorized)
    temp-blog-idea-20260115.md
    temp-call-sarah-20260115.md
  People/
    Colleagues/       ← Subcategory folders
      sarah-johnson.md
      alex-chen.md
    Family/
      mom-birthday.md
  Projects/
    Work/
      website-redesign.md
      quarterly-report.md
    Personal/
      blog-second-brain.md
      home-automation.md
  Ideas/
    Creative/
      poem-about-time.md
      short-story-outline.md
    Philosophical/
      consciousness-ai.md
      free-will-determinism.md
  Admin/
    Tasks/
      call-dentist.md
      buy-groceries.md
    MeetingNotes/
      standup-2026-01-14.md
      quarterly-planning.md
```

**Key Principles:**
- **File path IS the categorization** (category/subcategory/filename.md)
- One item = one file = one category/subcategory
- To recategorize = move file + update metadata
- **Filenames**: human-readable, no UUIDs, AI-proposed + user-confirmed
- **Subcategory folders**: created on-demand as needed

### Item Metadata Schema (YAML Frontmatter)

```yaml
---
# Identity
id: 550e8400-e29b-41d4-a716-446655440000  # UUID for DB primary key
title: "Second Brain with AI Integration"  # Display name

# Classification
category: Ideas                             # Inbox|People|Projects|Ideas|Admin
subcategory: Creative                       # Folder name, nullable
tags: [ai, productivity, blog, writing]    # Free-form keywords

# Timestamps
created: 2026-01-14T08:23:00Z
modified: 2026-01-15T14:30:00Z
last_worked: 2026-01-15T14:30:00Z          # Last content/metadata modification
categorized_at: 2026-01-14T09:00:00Z       # When moved from Inbox

# State & Surfacing
state: in-progress                          # uncategorized|not-started|in-progress|completed|archived
next_surface: 2026-01-16T07:00:00Z
cadence: daily                              # daily|weekly|monthly|custom (e.g., "3d", "2w")

# AI Metadata
confidence: 0.92                            # Classification confidence (0-1)
embedding_updated: 2026-01-15T14:31:00Z

# Privacy
no_ai: false                                # Exclude from AI processing

# Content hash for sync
content_hash: sha256:abc123...              # Detect external modifications
---

# Second Brain with AI Integration

[Content goes here...]

## Related
- [AI Integration Thoughts](Ideas/Philosophical/ai-consciousness.md) - Similar themes about AI
- [Website Redesign Project](Projects/Work/website-redesign.md) - Mentions blog platform
```

## Relationships

### Explicit Links (in content)
- Standard markdown links: `[Sarah Johnson](People/Colleagues/sarah-johnson.md)`
- Uses **file paths** (human-readable, not UUIDs)
- Bi-directional link detection (stored in DB)
- Links can break if files move → creates triage item for resolution

### Semantic Links (AI-generated)
- Added to "Related" section in markdown content
- Includes "why related" explanation
- AI regenerates periodically + on item modification
- User can manually edit this section
- Stored in `item_links` table with `link_type='semantic'`

### Example Related Section
```markdown
## Related
- [AI Integration](Ideas/Philosophical/ai-consciousness.md) - Similar themes
- [Website Redesign](Projects/Work/website-redesign.md) - Mentions blog
- [Productivity Reading](Admin/MeetingNotes/productivity-book.md) - Referenced concepts
```

### Hierarchy
- **Parent/child relationships**: Only for category → subcategory (folder structure)
- **Items are flat**: Relationships created through tags and links, not hierarchy
- No nested subcategories in MVP

## Database Schema (PostgreSQL + pgvector)

### Core Tables

```sql
-- Items: Core knowledge items
CREATE TABLE items (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  file_path TEXT UNIQUE NOT NULL,           -- e.g., "Ideas/Creative/blog-post.md"

  -- Classification
  category TEXT NOT NULL,                    -- enum: Inbox|People|Projects|Ideas|Admin
  subcategory TEXT,                          -- nullable, folder name
  tags TEXT[] DEFAULT '{}',                  -- array of tags

  -- State
  state TEXT NOT NULL DEFAULT 'uncategorized', -- enum: uncategorized|not-started|in-progress|completed|archived

  -- Timestamps
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_worked TIMESTAMPTZ,                   -- nullable, tracks actual work
  categorized_at TIMESTAMPTZ,                -- when moved from Inbox

  -- Surfacing
  next_surface TIMESTAMPTZ,
  cadence TEXT DEFAULT 'daily',              -- daily|weekly|monthly|3d|2w|etc

  -- AI
  confidence FLOAT,                          -- 0-1, classification confidence
  embedding VECTOR(1536),                    -- pgvector, dimension depends on model
  embedding_updated TIMESTAMPTZ,

  -- Privacy & Sync
  no_ai BOOLEAN DEFAULT FALSE,
  content_hash TEXT,                         -- sha256 for sync conflict detection

  -- Multi-tenant ready
  user_id UUID REFERENCES users(id),

  -- Indexes
  CONSTRAINT valid_confidence CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);

CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_state ON items(state);
CREATE INDEX idx_items_next_surface ON items(next_surface);
CREATE INDEX idx_items_tags ON items USING GIN(tags);
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_embedding ON items USING ivfflat(embedding vector_cosine_ops); -- or hnsw

-- Full-text search
ALTER TABLE items ADD COLUMN search_vector TSVECTOR;
CREATE INDEX idx_items_search ON items USING GIN(search_vector);

-- Item Links: Relationships between items
CREATE TABLE item_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  to_item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  link_type TEXT NOT NULL,                   -- 'explicit' | 'semantic'
  why_related TEXT,                          -- AI explanation for semantic links
  confidence FLOAT,                          -- for semantic links
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(from_item_id, to_item_id, link_type),
  CONSTRAINT no_self_links CHECK (from_item_id != to_item_id)
);

CREATE INDEX idx_item_links_from ON item_links(from_item_id);
CREATE INDEX idx_item_links_to ON item_links(to_item_id);

-- Users: Multi-tenant support
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  settings JSONB DEFAULT '{}'::jsonb         -- User preferences
);

-- User Config: Key-value configuration
CREATE TABLE user_config (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value JSONB NOT NULL,

  PRIMARY KEY(user_id, key)
);

-- Conversations: RRD-style progressive summarization
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  session_start TIMESTAMPTZ NOT NULL,
  session_end TIMESTAMPTZ,
  user_id UUID NOT NULL REFERENCES users(id),

  -- Progressive summarization tiers
  full_transcript JSONB,                     -- Last 7 days
  detailed_summary TEXT,                     -- 8-30 days
  brief_summary TEXT,                        -- 31-90 days
  key_outcomes TEXT,                         -- 90+ days

  detail_level TEXT NOT NULL DEFAULT 'full', -- 'full'|'detailed'|'brief'|'minimal'
  last_summarized TIMESTAMPTZ,
  changes_made JSONB                         -- What edits were applied
);

CREATE INDEX idx_conversations_item ON conversations(item_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_session ON conversations(session_start);

-- Prompts: Versioned AI prompts
CREATE TABLE prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,                 -- 'classification', 'summarization', etc.
  version INT NOT NULL,
  content TEXT NOT NULL,                     -- Prompt template
  model_config JSONB DEFAULT '{}'::jsonb,    -- Model settings (temperature, etc.)
  active BOOLEAN DEFAULT FALSE,
  created TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(name, version)
);

-- Token Usage: Cost tracking
CREATE TABLE token_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  operation TEXT NOT NULL,                   -- 'classification'|'embedding'|'conversation'
  model TEXT NOT NULL,                       -- Model identifier
  input_tokens INT NOT NULL,
  output_tokens INT NOT NULL,
  cost_usd DECIMAL(10,6),                    -- Estimated cost
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_token_usage_user ON token_usage(user_id);
CREATE INDEX idx_token_usage_timestamp ON token_usage(timestamp);

-- Audit Log: Change tracking
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  item_id UUID REFERENCES items(id),         -- nullable for system-level actions
  action TEXT NOT NULL,                      -- 'created'|'modified'|'categorized'|'moved'|etc
  before JSONB,                              -- State before change
  after JSONB,                               -- State after change
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_item ON audit_log(item_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
```

## Embedding & Semantic Search

### Embedding Strategy
- **What**: Full item (title + tags + content text)
- **When**: On creation/modification (async background job)
- **Model**: Via LiteLLM (e.g., text-embedding-3-small, configurable)
- **Storage**: pgvector column in items table
- **Dimension**: 1536 (OpenAI), 768 (sentence-transformers), configurable

### Use Cases
1. **Semantic similarity search**: "Show me items related to AI productivity"
2. **Auto-generate Related section**: Find semantically similar items
3. **Tag auto-suggestions**: Suggest tags based on content similarity
4. **Conversational queries**: "What have I written about meditation?"

### Query Example
```sql
-- Find top 10 most similar items to a given item
SELECT id, title, 1 - (embedding <=> $1) AS similarity
FROM items
WHERE user_id = $2 AND no_ai = FALSE
ORDER BY embedding <=> $1
LIMIT 10;
```

## Sync Architecture

### Principles
- **File system is source of truth**
- All changes written to files first
- Sync service reads files → updates database
- Database is derived/cached view for fast queries

### Bi-directional Sync Flow

**File → Database (External Edit):**
1. User edits file in Obsidian/VSCode
2. Sync service (Rust) detects file change via notify crate
3. Sync service reads raw file contents
4. Sync service computes content_hash (SHA-256)
5. Sync service calls POST /api/sync/file-changed with raw contents
6. API service parses markdown (frontmatter + content)
7. API service checks for conflicts (compare timestamps + hash)
8. API service updates database

**Database → File (Agent Edit):**
1. API service receives edit command
2. Acquires lock file (`{filename}.lock`)
3. Reads current file
4. Applies changes
5. Writes to temp file
6. Atomic rename (temp → actual)
7. Updates frontmatter metadata
8. Releases lock
9. Sync service detects change → updates DB (validates consistency)

### Conflict Resolution

**Conflict Detection:**
- Compare: file modified timestamp, DB modified timestamp, content_hash
- Conflict if: both changed since last sync, hashes differ

**Conflict Handling:**
1. Block further edits (set flag in DB, mark file as conflicted)
2. Write DB version to `{filename}.conflict-db.md`
3. Create triage item: "Resolve conflict: {item title}"
4. User resolves manually with diff tool
5. User tells agent "conflict resolved, accept current file"
6. Agent validates, clears conflict flag, resumes sync

**Edge Cases:**
- File moved externally: Attempt to resolve via item ID, else create triage item
- File deleted externally: Mark as archived in DB, create triage item for confirmation
- Multiple rapid edits: Lock files prevent corruption, last-write-wins after validation

## Tag Promotion & Emergent Taxonomy

### Monitoring
- Periodic job (daily/weekly) analyzes tag usage
- Detects semantic clusters using embeddings
- Identifies tags used across multiple items

### Promotion Criteria (TBD, iterate based on usage)
- Tag used on 10+ items
- High semantic similarity among tagged items
- Low overlap with existing subcategories
- User hasn't explicitly rejected promotion

### Promotion Flow
1. AI detects cluster (e.g., 15 items tagged #meditation)
2. Generates subcategory suggestion: "Ideas/Mindfulness"
3. Surfaces to user in digest or triage
4. User approves → creates subcategory folder, moves items, retains tags
5. User rejects → marks tag as "don't promote"

## To Explore Later

- Conflict resolution detailed workflow (merge strategies, auto-resolution heuristics)
- Tag promotion thresholds and algorithms (clustering methods, confidence scoring)
- Search query language/API design (natural language + structured queries)
- Audit log complete event types (define all trackable actions)
- User config keys and structure (evolve based on usage patterns)
- Advanced link types (parent/child, dependencies, sequences)
