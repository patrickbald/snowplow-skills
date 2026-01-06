# Snowplow Analytics Skills for Claude

A collection of specialized Claude Skills for implementing and working with Snowplow behavioral analytics. These skills extend Claude's capabilities with deep expertise in Snowplow tracking, data modeling, and analytics infrastructure.

## Overview

These skills enable Claude to provide expert guidance on Snowplow implementations, from schema design through data modeling and analytics. They're designed for technical teams implementing behavioral analytics with Snowplow.

## Available Skills

### 1. Snowplow Schema Design (`snowplow-schema-design.skill`)

Expert guidance for designing robust, maintainable Snowplow event and entity schemas.

**Use this skill when:**
- Creating new event schemas or entity/context schemas
- Deciding between event properties vs entities
- Planning schema evolution and versioning
- Establishing tracking taxonomies
- Implementing global contexts
- Validating schema structures

**Key features:**
- Event property vs entity property decision framework
- Schema abstraction spectrum guidance (specific to generic)
- Single-valued vs multi-valued entity patterns
- Global contexts and context generators
- Practical multi-event patterns (5 real-world patterns)
- Validation scripts included
- Anti-patterns to avoid

**Includes:**
- `validate_schema.py` - Validates Iglu structure, naming, constraints
- `test_event.py` - Send test events to Snowplow collector
- Complete schema examples reference

### 2. Snowplow dbt Modeling (`snowplow-dbt-modeling.skill`)

Comprehensive guidance for implementing Snowplow dbt data models and packages.

**Use this skill when:**
- Implementing Snowplow dbt packages (Unified, E-commerce, Media Player, Attribution)
- Creating custom behavioral data models
- Optimizing incremental processing strategies
- Configuring sessionization logic
- Modeling custom entities and SDEs
- Troubleshooting dbt model performance
- Setting up user stitching

**Key features:**
- Complete Unified Digital package configuration reference
- Custom model development patterns
- Incremental processing and manifest management
- Entity modeling (single vs multi-valued)
- Conversion tracking configuration
- User identity stitching strategies
- Performance optimization techniques
- Troubleshooting guide

**Includes:**
- Complete variable reference with examples
- Model outputs documentation (sessions, users, views)
- Configuration patterns for all major warehouses
- Performance tuning strategies

## Usage Examples

### Schema Design

```
User: I need to track user interactions with product carousels on my site. 
Should I put the carousel properties in the event or create an entity?

Claude: [Uses snowplow-schema-design skill]
I'd recommend creating a content_module entity for the carousel...
```

### dbt Modeling

```
User: How do I configure the Unified Digital package to track both web and 
mobile events with custom conversion tracking?

Claude: [Uses snowplow-dbt-modeling skill]
Here's how to configure the Unified package for your use case...
```

## Skill Development

These skills follow the [Snowplow Skills specification](https://docs.snowplow.io/docs/modeling-your-data/modeling-your-data-with-dbt/dbt-custom-models/dbt-skills/) and include:

- **SKILL.md**: Main documentation with structured guidance
- **scripts/**: Executable Python scripts for validation and testing
- **references/**: Detailed reference documentation

### File Structure

```
snowplow-schema-design/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   ├── validate_schema.py            # Schema validation
│   └── test_event.py                 # Event testing
└── references/
    └── schema_examples.md            # Complete examples

snowplow-dbt-modeling/
├── SKILL.md                          # Main skill documentation
└── references/
    └── unified_package.md            # Complete config reference
```

## Resources

- [Snowplow Documentation](https://docs.snowplow.io/)
- [Snowplow dbt Packages](https://docs.snowplow.io/docs/modeling-your-data/modeling-your-data-with-dbt/)
- [Snowplow Discourse Community](https://discourse.snowplow.io/)
- [Snowplow GitHub](https://github.com/snowplow)

## Support

For questions or issues:

- **Skill-related**: Open an issue in this repository
- **Snowplow product**: Contact Snowplow support or post in Discourse
- **Claude-related**: Refer to Anthropic's documentation

## License

These skills are provided as-is for use with Snowplow implementations. See individual skill files for specific licensing terms.

## Acknowledgments

These skills were developed based on:
- Real-world implementation patterns from Snowplow customers
- Official Snowplow documentation and best practices
- Feedback from Snowplow Technical Account Management team
- Community contributions and use cases

---

**Note**: These skills provide guidance and best practices but don't replace official Snowplow documentation or professional implementation services. Always validate recommendations against your specific requirements and the latest Snowplow documentation.