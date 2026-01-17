# UX Design

## CLI Interaction Model

### REPL Mode
**Conversational terminal interface** (inspired by Claude Code, Gemini CLI):
- Interactive, persistent session
- Multi-turn conversations
- Context maintained across turns
- Supports both conversational and command-driven interaction

### TUI Hybrid Approach
- **General conversation**: Plain text REPL (stdin/stdout)
- **Workflow modes**: Rich TUI panels (checkboxes, lists, navigation)
- Seamless transitions between modes

**Example:**
```bash
$ noosphere
Noosphere v0.1.0 | Vault: ~/noosphere-vault
Ready. What would you like to do?

> I need to call the dentist tomorrow
Captured. This looks like Admin > Tasks. Correct?

> yes
✓ Saved to Admin/Tasks/call-dentist-tomorrow.md
I'll remind you tomorrow at 7am.

> what needs categorizing?
[Switches to TUI triage mode]
```

## Context & Session Management

### Conversation Context
**Within a session:**
- **"it"/"that"** references last discussed item
- Multiple items can be **in focus** during general conversation
- Full session context for general flow
- **Constrained context** for workflow modes (triage, review, editing)
- **Explicit references** supported:
  - By ID: "work on abc-123"
  - By title: "work on my blog post"
  - By description: "the dentist task"

**Example:**
```bash
> I need to write a blog post about AI
Captured. Looks like Ideas > Creative. Correct?

> yes

> also need to research embeddings for it
Captured. This seems related to the blog post. Link them?

> yes
✓ Linked "Research embeddings" to "Blog post about AI"
```

### Session Persistence
- **Context summarized** across restarts (not full history)
- **Pinned items** (#remember-style) loaded on restart
- **Work-in-progress state** preserved
- **Session file** stores:
  - Active mode (if any)
  - Pinned items
  - Recent context summary

**Example:**
```bash
> #remember the blog post and dentist task

# Later, after restart:
$ noosphere
Noosphere v0.1.0 | Vault: ~/noosphere-vault
Welcome back. You have 2 pinned items:
- Blog post about AI (Ideas/Creative)
- Call dentist tomorrow (Admin/Tasks)

Ready. What would you like to do?
```

## Workflow Modes

### 1. Triage Mode (`/triage`)

**Purpose:** Categorize uncategorized items from Inbox

**Entry:**
- Explicit: `/triage` command
- Auto-detect: "what needs categorizing?" or "show me inbox"
- Scheduled: Automatic at morning digest time (if items pending)

**UI:** TUI panel with checkboxes

```
════════════════════════════════════════════════════════
TRIAGE MODE - 15 uncategorized items
════════════════════════════════════════════════════════

[ ] "meditation breathing technique I read about"
    💡 AI: Ideas > Wellness
    🏷️  Tags: #meditation #breathing #health
    ✅ Confidence: 89%

[ ] "call Sarah about website project deadline"
    💡 AI: Admin > Tasks
    🏷️  Tags: #sarah #website #deadline
    ✅ Confidence: 92%

[x] "blog post idea about second brain"
    💡 AI: Ideas > Creative
    🏷️  Tags: #blog #writing #productivity
    ✅ Confidence: 95%

...

Actions: [↑↓] navigate [space] toggle [enter] approve checked
         [m] modify selected [d] defer selected [q] quit
```

**Workflow:**
1. Display all uncategorized items with AI suggestions
2. User reviews and checks items to approve
3. **Bulk approve**: Checked items → move to suggested categories
4. **Unchecked items**: Conversational refinement
   - Agent: "What should we do with 'meditation breathing technique'?"
   - User: "This should be Ideas > Wellness"
   - Or: "I'm not sure, defer it"
5. Exit anytime → remaining items stay in Inbox for next session

**Conversational Fallback:**
```
[After bulk approval, 3 items remain unchecked]

Switching to conversation for remaining items.

Item 1/3: "meeting notes from standup"
AI suggested: Admin > MeetingNotes
Why did you skip this?

> it's actually about a person, Sarah
Got it. Let me recategorize...
New suggestion: People > Colleagues > Sarah
Better?

> yes
✓ Saved to People/Colleagues/sarah-standup-notes.md
```

### 2. Review Mode (`/review`)

**Purpose:** Review categorized items surfacing today, decide what to work on

**Entry:**
- Explicit: `/review` command
- Auto-detect: "what's due today?" or "show me review"
- Scheduled: Morning digest (if user configured)

**UI:** TUI panel with item list

```
════════════════════════════════════════════════════════
REVIEW MODE - Wednesday, Jan 15, 2026
════════════════════════════════════════════════════════

DUE TODAY (8 items)
[ ] Call dentist - Admin/Tasks
[ ] Finish quarterly report - Admin/Tasks
    (In progress, last worked: 3 days ago)
[ ] Follow up with Sarah - People/Colleagues

RESURFACING (12 items)
[ ] Blog post: Second brain AI - Ideas/Creative
    (In progress, last worked: 2 days ago)
    💬 AI: Added outline and 2 draft paragraphs
[ ] Meditation practice research - Ideas/Wellness
    (Not started)
[ ] Website redesign project - Projects/Work
    (In progress, last worked: 5 days ago)
    💬 AI: Updated timeline, researched hosting options

...

Actions: [↑↓] navigate [space] toggle [enter] work on
         [d] defer all checked [c] complete checked [q] quit
```

**Actions:**
- **Work on item**: Select → transitions to editing mode (review suspends)
- **Defer**: Tomorrow or user's cadence (not manually set)
- **Complete/Archive**: Mark done
- **Batch defer**: Check multiple, defer all at once

**Work Transition:**
```
[User selects "Blog post: Second brain AI" and presses Enter]

Opening: Blog post: Second brain AI
[Review mode suspends, enters editing mode]

Current content (523 words):
# Second Brain with AI Integration
[outline + 2 paragraphs...]

Last worked: 2 days ago
State: in-progress

What would you like to work on?

> help me expand the introduction

[Conversational editing session...]

> done
✓ Saved changes to Ideas/Creative/blog-post-second-brain.md
Marked as in-progress, deferred to tomorrow.

[Returns to review mode]

════════════════════════════════════════════════════════
REVIEW MODE - 19 items remaining
════════════════════════════════════════════════════════
[continues review...]
```

### 3. Content Editing Mode

**Purpose:** Develop item content conversationally

**Triggered:**
- From review mode: select item and press Enter
- Direct: "work on blog post" or "edit the dentist task"

**UI:** Split-panel TUI (future: may start simpler)

```
┌─────────────────────────┬─────────────────────────────┐
│ CONVERSATION            │ DOCUMENT PREVIEW            │
├─────────────────────────┼─────────────────────────────┤
│                         │ # Second Brain with AI      │
│ What would you like to  │                             │
│ work on?                │ ## Introduction             │
│                         │ Personal knowledge...       │
│ > expand introduction   │                             │
│                         │ ## Core Concept             │
│ I suggest adding:       │ [outline...]                │
│                         │                             │
│ ++ The challenge with   │ ## Related                  │
│ ++ traditional note     │ - AI Integration Thoughts   │
│ ++ systems is...        │                             │
│                         │                             │
│ Apply? (y/n)           │                             │
│ > y                     │                             │
│                         │                             │
│ ✓ Applied changes       │ # Second Brain with AI      │
│                         │                             │
│ Anything else?          │ ## Introduction             │
│                         │ Personal knowledge...       │
│                         │ ++ The challenge with       │
│                         │ ++ traditional note...      │
└─────────────────────────┴─────────────────────────────┘
```

**Workflow:**
1. User selects item to work on
2. New context created, item content loaded
3. **Conversation history loaded** (from DB, summarized if old)
4. Multi-turn dialogue for content development
5. **Agent shows proposed changes** in right panel (diff highlighting)
6. User approves → **immediate write to file** (with lock)
7. **Auto-detect completion**: Agent asks "Anything else?" or user types "done"
8. Updates: `last_worked` timestamp, defers to tomorrow, state = in-progress
9. **Conversation saved to DB** (for future context)
10. Returns to review mode (if came from there) or general conversation

**Clarifying Questions:**
```
> expand the introduction

I see the document doesn't have a section labeled "Introduction".
Did you mean:
1. The first paragraph (starts with "Personal knowledge...")
2. Add a new Introduction section before the current content
3. Something else

> 1

Got it. I'll expand the first paragraph. Here's what I suggest:
[shows changes...]
```

**Features:**
- Diff highlighting (additions in green, deletions in red)
- Real-time preview as changes approved
- Undo not supported in MVP (rely on git/file history)
- Conversation context preserved across sessions

### 4. Planning Mode

**Deferred**: Define requirements later based on MVP usage

**Potential use cases:**
- Help break down projects into tasks
- Generate next actions from project notes
- Link related items into project workflow
- Timeline/milestone planning

## Mode Entry Methods

**All three methods work:**

1. **Explicit commands:**
   - `/triage` - Enter triage mode
   - `/review` - Enter review mode
   - `/edit [item]` or `work on [item]` - Enter editing mode
   - `/search [query]` - Search items (future)

2. **Auto-detect:** Agent infers from conversation
   - "what needs categorizing?" → triage mode
   - "what's due today?" → review mode
   - "show me blog posts" → search/query
   - "work on dentist task" → editing mode

3. **Scheduled:** System-initiated
   - Morning digest triggers review/triage if items pending
   - Periodic prompts for long-dormant items

## General Conversation Patterns

### Capture
```
> I need to follow up with Sarah about the website
Captured. This looks like People > Colleagues. Correct?

> yes
✓ Saved to People/Colleagues/sarah-website-followup.md
```

### Batch Capture
```
> Capture these items: dentist appointment, finish report, meditation idea
Got it. Processing 3 items...

1. "dentist appointment" → Admin > Tasks ✓
2. "finish report" → Admin > Tasks ✓
3. "meditation idea" → Ideas > Wellness ✓

All saved. Want to categorize now or later?

> later
```

### Query
```
> what have I written about AI?
Found 8 items:
1. Blog post: Second brain AI (Ideas/Creative) - in progress
2. AI consciousness notes (Ideas/Philosophical) - not started
3. ChatGPT productivity tips (Admin/MeetingNotes) - archived
...

Want to work on any of these?
```

### Recategorize
```
> move the dentist task to Projects
Moving "Call dentist" from Admin/Tasks to Projects...

Just to confirm - is this part of a larger project?
Or should I create a new subcategory?

> it's just a one-off task, keep it in Admin
Understood. Keeping in Admin/Tasks.
```

## Future UX Enhancements

### Split-Panel Refinements
- **Right panel features**:
  - Syntax highlighting for code
  - Live markdown preview
  - Line numbers
  - Fold/unfold sections
  - Jump to section
- **Left panel features**:
  - Command history (↑↓ to recall)
  - Autocomplete for items/tags
  - Inline help (?command)

### Keyboard Shortcuts
- `Ctrl+T` - Triage mode
- `Ctrl+R` - Review mode
- `Ctrl+E` - Edit last referenced item
- `Ctrl+F` - Search
- `Ctrl+P` - Command palette
- `Ctrl+L` - Clear screen
- `Esc` - Exit mode / Cancel

### Advanced Interactions
- Drag-and-drop items in TUI
- Multi-select across modes
- Filtered views (by tag, category, date)
- Custom saved views
- Bulk operations (tag, move, archive)

### Accessibility
- Screen reader support
- High-contrast mode
- Configurable font sizes
- Audio feedback for actions

## Error Handling

### Graceful Degradation
- **AI unavailable**: Allow manual categorization, queue classification for later
- **Database down**: Read-only mode from files, warn user
- **File conflicts**: Clear messaging, easy resolution flow
- **Sync failures**: Retry with exponential backoff, notify user

### User-Friendly Errors
```
# Bad:
Error: DatabaseConnectionError at line 42 in sync.py

# Good:
⚠️  Can't connect to database. Your files are safe.
   Try: noosphere check-db
   Or: Contact support at support@noosphere.app
```

### Validation
- Prevent invalid file moves (check category/subcategory exists)
- Warn on potentially destructive actions (archive project with active tasks)
- Confirm before bulk operations (defer all 50 items?)

## Onboarding / First Run

**Initial Setup Flow:**
1. Welcome message, explain core concepts (30 seconds)
2. Create vault directory, initialize DB
3. Quick tutorial: capture, triage, review (5 minutes)
4. Optional: import from existing tools (Notion, Obsidian)

**Guided First Actions:**
```
Welcome to Noosphere! Let's capture your first thought.

Try typing something like:
- "I need to buy groceries"
- "Follow up with Alice about project"
- "Blog post idea about productivity"

> I need to buy groceries

Great! I think this is Admin > Tasks. Correct?

> yes

Perfect. You've captured your first item!
Let's try one more...
```
