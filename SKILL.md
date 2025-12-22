---
name: snowplow-tracking
description: Expert guidance for implementing Snowplow Analytics tracking including schema design, tracker setup, event instrumentation, and debugging. Use when implementing Snowplow tracking, designing event or context schemas, configuring trackers (JavaScript, mobile, server-side), troubleshooting tracking issues, or migrating from other analytics platforms.
---

# Snowplow Analytics Implementation

## Quick reference

**Schema design** → Read [schemas/DESIGN.md](schemas/DESIGN.md)
**JavaScript tracker** → Read [trackers/JAVASCRIPT.md](trackers/JAVASCRIPT.md)
**Mobile trackers** → Read [trackers/MOBILE.md](trackers/MOBILE.md)
**Server-side** → Read [trackers/SERVER_SIDE.md](trackers/SERVER_SIDE.md)
**Testing** → Read [testing/VALIDATION.md](testing/VALIDATION.md)
**Migrations** → Read [migration/GUIDE.md](migration/GUIDE.md)
**Debugging** → Read [troubleshooting/DEBUG.md](troubleshooting/DEBUG.md)

## Core principles

1. **Schema-first**: Define schemas before implementing tracking
2. **Consistent naming**: Use object_action pattern (e.g., `product_viewed`, `form_submitted`)
3. **Context enrichment**: Attach relevant contexts to events
4. **Validation at every stage**: Schema validation, dev testing, production monitoring
5. **Test before production**: Use `scripts/test_event.py` to validate events

## Standard workflow

1. Design event and context schemas
2. Validate schemas: `python scripts/validate_schema.py schema.json`
3. Register schemas in Iglu repository
4. Implement tracking code
5. Test in development
6. Monitor in production

## Schema templates

### Event schema
```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.yourcompany",
    "name": "event_name",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "property_name": {
      "type": "string",
      "description": "Clear description",
      "maxLength": 500
    }
  },
  "required": ["property_name"],
  "additionalProperties": false
}
```

### Context schema
Same structure as event schema, but describes reusable entity properties.

## JavaScript tracker basics
```javascript
import { newTracker, trackSelfDescribingEvent } from '@snowplow/browser-tracker';

newTracker('sp', 'collector.yourcompany.com', {
  appId: 'your-app',
  contexts: { webPage: true, session: true }
});

trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.yourcompany/event_name/jsonschema/1-0-0',
    data: { /* your event properties */ }
  }
});
```

For complete setup and patterns, read [trackers/JAVASCRIPT.md](trackers/JAVASCRIPT.md).

## Helper scripts

All scripts are in `scripts/` directory:

**validate_schema.py**: Validate JSON schema syntax and Snowplow conventions
```bash
python scripts/validate_schema.py your_schema.json
```

**test_event.py**: Send test event to collector
```bash
python scripts/test_event.py --collector your-collector.com --schema iglu:com.company/event/jsonschema/1-0-0 --data '{"key":"value"}'
```

**generate_tracker_code.py**: Generate tracker implementation from schema
```bash
python scripts/generate_tracker_code.py schema.json --language javascript
```

## Common patterns

### E-commerce tracking
```javascript
// Product viewed
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/product_viewed/jsonschema/1-0-0',
    data: {
      product_id: 'PROD-123',
      price: 99.99,
      currency: 'USD'
    }
  }
});
```

### Form tracking
```javascript
// Form submitted
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/form_submitted/jsonschema/1-0-0',
    data: {
      form_id: 'signup-form',
      fields_completed: 5,
      time_to_complete_seconds: 45
    }
  }
});
```

## Schema versioning

Version format: `MODEL-REVISION-ADDITION`

- **MODEL (1-x-x)**: Breaking changes
- **REVISION (x-1-x)**: Add optional fields
- **ADDITION (x-x-1)**: Documentation only

### Breaking changes (bump MODEL)
- Remove required fields
- Change field types
- Make optional fields required
- Stricter validation

### Non-breaking changes (bump REVISION)
- Add optional fields
- Make required fields optional
- Loosen validation

## Debugging checklist

1. Check collector endpoint is reachable
2. Verify schema is registered in Iglu
3. Validate event structure matches schema
4. Check browser console for tracker errors
5. Use Snowplow Inspector browser extension
6. Review collector logs

For detailed debugging, read [troubleshooting/DEBUG.md](troubleshooting/DEBUG.md).