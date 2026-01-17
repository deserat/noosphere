# Multi-Agent Development Workflow

This directory contains documentation for multi-agent collaborative development on the Noosphere project. It establishes patterns, standards, and architectural decisions that AI coding assistants should follow when working on different services.

## Overview

Noosphere is designed to support **parallel development by multiple AI agents**, each with specific expertise and responsibilities. This approach enables:

- **Faster Development**: Multiple agents work simultaneously on different services
- **Domain Expertise**: Each agent specializes in specific areas (backend, frontend, security, etc.)
- **Clean Boundaries**: Service-specific `AGENTS.md` files define responsibilities
- **Consistent Patterns**: Shared standards across all services

## Multi-Agent Architecture

### Service-Specific Agents

Each service has its own `AGENTS.md` file defining:
- **Service Boundaries**: What this service is responsible for
- **API Contracts**: How this service communicates with others
- **Patterns**: Service-specific coding conventions
- **Dependencies**: External services and libraries

**Service Context Files**:
- [`api-service/AGENTS.md`](../../api-service/AGENTS.md) - Backend API, AI, scheduler
- [`cli/AGENTS.md`](../../cli/AGENTS.md) - Rust CLI with ratatui TUI
- [`sync-service/AGENTS.md`](../../sync-service/AGENTS.md) - File watching and sync

### Global Context

Shared knowledge across all agents:
- [`architecture.md`](architecture.md) - System-wide architectural decisions
- [`standards.md`](standards.md) - Python and Rust coding standards

## Agent Workflow

### 1. Starting Work on a Service

When an AI agent begins work on a service:

```markdown
1. Read service-specific AGENTS.md for context
2. Review architecture.md for system-wide decisions
3. Check standards.md for coding conventions
4. Understand service boundaries and responsibilities
5. Begin implementation within defined scope
```

### 2. Cross-Service Communication

When services need to interact:

```markdown
1. Check API contracts in respective AGENTS.md files
2. Use defined REST endpoints or file-based communication
3. Never directly access another service's internals
4. Document new integration points in AGENTS.md
```

### 3. Making Architectural Decisions

When facing architectural choices:

```markdown
1. Check if decision is service-specific or system-wide
2. Service-specific: Document in service AGENTS.md
3. System-wide: Consult architecture.md, propose changes if needed
4. Always justify decisions with rationale
```

## Example Workflow: Adding Authentication

This example shows how multiple agents collaborate on adding authentication:

### Agent 1: Backend (API Service)

**Context**: Read `api-service/AGENTS.md`

**Responsibilities**:
1. Implement JWT authentication middleware
2. Create user authentication endpoints
3. Add authentication to database models
4. Document API authentication in AGENTS.md

**Boundaries**:
- ✅ Implement backend authentication logic
- ✅ Provide JWT tokens via API endpoints
- ❌ Don't modify CLI or sync service code
- ❌ Don't assume how clients will store tokens

### Agent 2: CLI (Client)

**Context**: Read `cli/AGENTS.md`

**Responsibilities**:
1. Add login UI in TUI (ratatui)
2. Store JWT token securely (OS keyring)
3. Include token in API requests
4. Handle token expiration and refresh

**Boundaries**:
- ✅ Implement client-side auth UI
- ✅ Consume authentication API endpoints
- ❌ Don't implement authentication logic (server responsibility)
- ❌ Don't modify API service code

### Agent 3: Security Review

**Context**: Read `architecture.md` for security principles

**Responsibilities**:
1. Review JWT implementation
2. Check for common vulnerabilities (OWASP Top 10)
3. Validate token storage security
4. Document security decisions

**Coordination**:
- Review both agents' work
- Provide feedback via comments
- Update architecture.md with security patterns

## Communication Patterns

### File-Based Coordination

Agents communicate via well-defined files:

```
docs/agents/
  ├── README.md          # This file - workflow guide
  ├── architecture.md    # System-wide decisions
  └── standards.md       # Coding conventions

api-service/
  └── AGENTS.md          # Backend service context

cli/
  └── AGENTS.md          # CLI service context

sync-service/
  └── AGENTS.md          # Sync service context
```

### Decision Documentation

All architectural decisions follow this format:

```markdown
## Decision: [Title]

**Date**: YYYY-MM-DD
**Decider**: [Agent/Team]
**Status**: Accepted | Proposed | Deprecated

### Context
[Why was this decision needed?]

### Decision
[What did we decide?]

### Rationale
[Why this approach over alternatives?]

### Consequences
- Positive: [Benefits]
- Negative: [Trade-offs]
- Risks: [Potential issues]
```

## Best Practices

### For AI Agents

1. **Always Read Context First**: Start by reading relevant AGENTS.md files
2. **Stay Within Boundaries**: Don't modify code outside your service
3. **Document Decisions**: Update AGENTS.md with new patterns
4. **Communicate Changes**: Document API changes that affect other services
5. **Test Integration**: Verify changes work with other services

### For Service Boundaries

**Clean Separation**:
- Each service is independently deployable
- No shared code between services
- Communication via REST API or file watching
- Each service has its own dependencies

**API Contracts**:
- REST API for client-server communication
- File-based events for vault synchronization
- Documented in AGENTS.md files
- Versioned for backward compatibility

### For Parallel Development

**Independent Work**:
- Services can be developed in parallel
- Minimal cross-service dependencies
- Mock other services for testing
- Clear API contracts enable parallel work

**Coordination Points**:
- Regular sync via AGENTS.md updates
- Architecture.md for system-wide changes
- Integration testing after feature completion
- Code review before merging

## Tools and Automation

### Agent Memory System

Agents use Serena MCP for cross-session memory:

```yaml
Session Context:
  - write_memory("api-service/context", service_state)
  - read_memory("api-service/context") → Restore state

Pattern Learning:
  - write_memory("patterns/fastapi-auth", implementation)
  - read_memory("patterns/fastapi-auth") → Reuse pattern

Mistake Prevention:
  - write_memory("mistakes/jwt-security", lesson_learned)
  - read_memory("mistakes/jwt-security") → Avoid repeat
```

### Quality Gates

Before completing work:

```markdown
1. Code compiles without errors
2. Tests pass (unit + integration)
3. Documentation updated (AGENTS.md, code comments)
4. Follows coding standards (standards.md)
5. API contracts documented if changed
6. Cross-service integration verified
```

## Getting Started

### New Agent Onboarding

1. Read this README.md for workflow overview
2. Read architecture.md for system architecture
3. Read standards.md for coding conventions
4. Choose a service to work on
5. Read that service's AGENTS.md for context
6. Start with Phase 1 user stories
7. Document decisions and patterns as you work

### Contributing to Documentation

When you discover new patterns or make decisions:

1. **Service-Specific**: Update service's AGENTS.md
2. **Cross-Service**: Update architecture.md
3. **Coding Patterns**: Update standards.md
4. **Workflow Improvements**: Update this README.md

## Resources

- [Implementation Roadmap](../project/implementation-roadmap.md)
- [User Stories](../project/stories/README.md)
- [Setup Guide](../setup.md)
- [Architecture Decisions](architecture.md)
- [Coding Standards](standards.md)

## Questions and Feedback

For questions about the multi-agent workflow:
- Create an issue on GitHub
- Update this documentation with clarifications
- Propose improvements to the workflow
