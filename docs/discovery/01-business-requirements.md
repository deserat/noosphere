# Business Requirements

## Core User Workflows

### 1. Capture (Frictionless)
- **Surfaces**: CLI (MVP), later: Gnome applet, Slack, web, mobile, OCR, diagrams
- **Input**: Raw thought, any medium, zero decisions required
- **Frequency**: 2-30 captures/day (some power users 0-100/day)
- **Key Principle**: One action to capture, no categorization decisions

### 2. Classify (AI-Powered)
- **AI Provider**: LiteLLM (provider-agnostic)
- **Classification Hierarchy**:
  - **Top-level** (5 categories): Inbox, People, Projects, Ideas, Admin
  - **Subcategories** (emergent): Created organically based on content patterns
  - **Tags** (folksonomy): Free-form keywords for relationships
- **Tag Promotion**: AI suggests subcategory creation when tags gain semantic importance
- **Relationships Detected**:
  - Semantic similarity
  - Entity references
  - Project connections
  - Temporal clustering

### 3. Triage & Categorize (Next Day)
**Categorization is mandatory but deferrable**

**Interface shows**:
- Original captured text
- AI suggestions (category + subcategory + tags)
- Confidence score

**User actions**:
- Accept (1-click or checkbox for bulk)
- Modify category/subcategory/tags (conversational)
- Add own tags
- Defer categorization to future date

**Surfaces**: CLI with TUI panel (checkboxes)

### 4. Surface (Configurable Cadence)
**Resurfacing rules cascade**:
```
Base: Next day (default)
  ↓ overridden by
General Rule: User preference (e.g., every 3 days)
  ↓ overridden by
Category Rule: Per-category cadence (e.g., Tasks daily, Ideas weekly)
  ↓ overridden by
Item Field: Specific date/schedule on item
```

**MVP Surfacing Modes**:
- Batch morning digest (configurable time)
- On-demand review (`noosphere review` or `/review`)

**Later**: Progressive surfacing throughout day, scheduled to specific surfaces

### 5. Work & Develop
**Item States**:
- **Uncategorized**: In Inbox, needs triage
- **Not started**: Categorized, never modified
- **In progress**: Modified since categorization
- **Completed**: Explicitly marked done
- **Archived**: Put away

**"Work" = Modify**: Content or metadata changes
- Updates last_worked timestamp
- AI summarizes changes when item resurfaces
- Automatically defers to tomorrow (or user cadence)

**Dual Editing Modes**:
1. **File-based**: Markdown files in vault, any external tool can edit (Obsidian, VSCode, etc.)
2. **Conversational**: AI agent helps develop content through dialogue

## Emergent Taxonomy

**Core Concept**: System learns organizational structure from usage patterns

- **Categories**: Fixed (Inbox, People, Projects, Ideas, Admin)
- **Subcategories**: Emerge organically from content patterns
- **Tags**: Free-form, AI-suggested, user-added
- **Promotion Path**: Tag → (gains semantic importance) → AI suggests subcategory creation

**Example evolution**:
1. Day 1: "meditation breathing" → tags: #meditation #breathing
2. Week 2: 10 items tagged #meditation → AI: "Create subcategory 'Ideas/Mindfulness'?"
3. User approves → All #meditation items move to new subcategory, tags retained

## Performance Requirements

### Latency Targets
- **Capture → storage**: < 100ms (once API receives)
- **Classification**: < 5 seconds
- **Digest generation**: < 5 seconds per user
- **Agent processing indicator**: < 300ms (show thinking/working)

### Scale Targets (Future)
- **Users**: 10K
- **Items per user**: 100 average, some users 100K
- **Daily captures**: 0-100 per user (typical 2-30)
- **Uptime**: 99.9%
- **Region**: Single region initially

## Privacy & Data Ownership

- **Local-first option**: Offline support, data on device
- **Export**: Full markdown export (native format)
- **Encryption**: At rest in cloud (future)
- **AI Privacy**:
  - Service processes all content by default
  - `#no-ai` tag excludes from agent/AI processing
  - BYO AI configuration (later feature)

## Productization Strategy

### Target Market
- **Primary**: Knowledge workers broadly (anyone with knowledge management needs)
- **Personas**: Writers, researchers, consultants, engineers, entrepreneurs
- **Pain Point**: Existing tools (Notion, Obsidian, Evernote) too high-friction

### Revenue Model
- **Freemium + tiered subscriptions**
- **Tier Differentiation**:
  - AI features and usage limits
  - AI call quotas
  - Capture surfaces access (web, mobile, etc.)
- **Timeline**: Build for personal use (1 month), architect for scale from day 1
- **Future Tiers**: TBD based on usage patterns

### Competitive Positioning
- **vs. Notion**: Local-first, conversational interface, zero-friction capture
- **vs. Obsidian**: Built-in AI, automatic categorization, proactive surfacing
- **vs. Roam/LogSeq**: Simpler mental model, emergent vs. manual structure
- **Unique Value**: AI agent IS the interface, not a bolt-on feature

## Non-Functional Requirements

### Reliability
- 99.9% uptime (future cloud)
- Graceful degradation when AI unavailable
- Data integrity (file + DB consistency)
- Conflict resolution that doesn't lose data

### Usability
- < 10 minutes to triage 30 items
- < 5 seconds perceived response time
- Zero-learning curve for capture
- Keyboard-driven power-user mode

### Maintainability
- Clear separation of concerns (file, DB, AI)
- Testable components
- Database migrations (Alembic)
- Error tracking (Sentry)

### Security (Future Cloud)
- Encryption at rest
- Secure API communication
- User authentication/authorization
- Data isolation (multi-tenant)
