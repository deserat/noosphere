# Noosphere - Second Brain MVP

## Vision
**Obsidian + Cloud Sync + Conversational AI**

A personal knowledge management system that eliminates capture friction through AI-powered classification, provides multi-device cloud sync, and enables conversational content development.

## Problem Statement
Users lose thoughts and information due to:
1. **Capture friction** - categorization decisions, device switching, medium constraints
2. **Sorting burden** - manual organization is overwhelming
3. **Utilization gap** - captured items don't get surfaced or acted upon

## Success Criteria (3 months)
- Capturing 2-30 items daily with zero friction
- Items automatically categorized and resurfaced until dealt with
- Following up on work commitments consistently
- Developing ideas into documents (blog posts, stories, applications)
- Personal projects and creative work progressing incrementally

## MVP Scope: Local-First, Cloud-Ready

**MVP runs entirely on local system:**
- Local database/storage
- Local API service (Python with integrated scheduler)
- Local client services (Rust CLI + sync-service)
- Local AI calls (via LiteLLM)
- Local file vault

**Architected for cloud migration:**
- Component boundaries designed for distributed deployment
- Message passing patterns (can become Pub/Sub)
- Database abstraction (can swap local → Cloud SQL/Firestore)
- Authentication/multi-tenancy structure ready (but single-user initially)

## Primary Interface: Conversational Agent

**CRITICAL**: The conversational agent IS the system, not a feature.

All interaction happens via natural language conversation:
- **Capture**: "I need to call the dentist tomorrow"
- **Triage**: "Show me items to categorize"
- **Edit**: "Help me develop that blog post idea"
- **Query**: "What's due today?"
- **All workflows**: Through dialogue

## Documentation Structure

- **[Business Requirements](01-business-requirements.md)** - Workflows, user journeys, productization
- **[Information Architecture](02-information-architecture.md)** - File structure, metadata, database schema
- **[UX Design](03-ux-design.md)** - CLI interaction, workflow modes, TUI patterns
- **[Technical Architecture](04-technical-architecture.md)** - System components, APIs, services
- **[Implementation Plan](05-implementation-plan.md)** - Phases, validation, next steps
