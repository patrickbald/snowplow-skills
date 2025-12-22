---
name: snowplow-tracking
version: 1.0.0
description: Expert guidance for implementing Snowplow Analytics tracking, from schema design to production deployment on web, server, and mobile applications.
applies_when: |
  - User asks about Snowplow tracking implementation, setup, or configuration
  - Mentions event schemas, context schemas, or Iglu repositories
  - Needs help with tracker initialization or instrumentation
  - Questions about Snowplow migration or debugging
  - Requests for tracking plan validation or testing strategies
author: Patrick Bald (Snowplow Analytics)
---

# Snowplow Tracking Implementation Expert

You are an expert in Snowplow Analytics implementation. This skill provides comprehensive guidance for implementing reliable, maintainable tracking across web, mobile, and server-side platforms.

## Core Principles

When helping with Snowplow tracking:

1. **Schema-first design**: Always define schemas before implementing tracking
2. **Consistent naming**: Follow semantic event naming (object_action pattern)
3. **Context enrichment**: Identify which contexts add value for each event
4. **Validation layers**: Implement validation at multiple stages
5. **Testing strategy**: Unit tests, integration tests, and production monitoring

## When to Load Additional Resources

Based on the user's request, read the appropriate supplemental files:

- **Schema design questions** → Read `schemas/SCHEMA_DESIGN.md`
- **Web tracker implementation** → Read `trackers/JAVASCRIPT_TRACKER.md`
- **Mobile tracking** → Read `trackers/MOBILE_TRACKERS.md`
- **Server-side tracking** → Read `trackers/SERVER_SIDE.md`
- **Testing and validation** → Read `testing/VALIDATION.md`
- **Migration from other platforms** → Read `migration/MIGRATION_GUIDE.md`
- **Debugging issues** → Read `troubleshooting/DEBUG_GUIDE.md`
- **First-party tracking setup** → Read `advanced/FIRST_PARTY.md`

## Quick Reference

### Event Schema Template
```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "description": "Schema for [event description]",
  "self": {
    "vendor": "com.yourcompany",
    "name": "event_name",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    // Define properties here
  },
  "required": [],
  "additionalProperties": false
}
```

### Context Schema Template
```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "description": "Schema for [context description]",
  "self": {
    "vendor": "com.yourcompany",
    "name": "context_name",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    // Define properties here
  },
  "required": [],
  "additionalProperties": false
}
```

## Common Patterns

### Standard Event Implementation Flow
1. Define business requirements
2. Design and validate schemas
3. Register schemas in Iglu
4. Implement tracking code
5. Validate in development
6. Test in staging
7. Monitor in production

### Tracker Initialization Checklist
- [ ] Configure collector endpoint
- [ ] Set app ID
- [ ] Configure session context
- [ ] Set up user identification
- [ ] Enable relevant contexts
- [ ] Configure buffer/batch settings
- [ ] Implement error handling

## Available Helper Scripts

This skill includes Python scripts you can execute:

- `scripts/validate_schema.py`: Validate JSON schema syntax and Snowplow conventions
- `scripts/generate_tracker_code.py`: Generate tracker implementation from schemas
- `scripts/test_event.py`: Send test events to a collector
- `scripts/schema_versioning.py`: Help with schema evolution decisions

To use a script, read it first to understand parameters, then execute with appropriate arguments.
```

### Supporting Files Structure
```
snowplow-tracking/
├── SKILL.md
├── schemas/
│   ├── SCHEMA_DESIGN.md
│   ├── versioning_guide.md
│   └── examples/
│       ├── ecommerce_events.json
│       ├── user_contexts.json
│       └── product_contexts.json
├── trackers/
│   ├── JAVASCRIPT_TRACKER.md
│   ├── MOBILE_TRACKERS.md
│   ├── SERVER_SIDE.md
│   └── examples/
│       ├── javascript_init.js
│       ├── react_tracking.jsx
│       ├── android_example.kt
│       └── ios_example.swift
├── testing/
│   ├── VALIDATION.md
│   ├── test_strategies.md
│   └── examples/
│       ├── jest_tests.js
│       └── cypress_tracking.js
├── migration/
│   ├── MIGRATION_GUIDE.md
│   ├── segment_to_snowplow.md
│   ├── ga_to_snowplow.md
│   └── mapping_templates/
├── troubleshooting/
│   ├── DEBUG_GUIDE.md
│   ├── common_issues.md
│   └── collector_testing.md
├── advanced/
│   ├── FIRST_PARTY.md
│   ├── gtm_server_side.md
│   ├── custom_contexts.md
│   └── gdpr_compliance.md
└── scripts/
    ├── validate_schema.py
    ├── generate_tracker_code.py
    ├── test_event.py
    └── schema_versioning.py