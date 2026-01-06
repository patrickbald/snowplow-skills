---
name: snowplow-schema-design
description: Expert guidance for designing Snowplow event and entity schemas following best practices for naming, structure, validation rules, versioning, and design decisions. Use when creating new event schemas, designing entity/context schemas, deciding between event properties vs entities, planning schema evolution, determining abstraction levels, implementing global contexts, validating schema structures, or establishing tracking taxonomies for behavioral analytics implementations.
---

# Snowplow Schema Design

Expert guidance for creating robust, maintainable Snowplow schemas with practical design patterns.

## Quick Reference

- **Event schemas** → Define self-describing events with clear business meaning
- **Entity schemas** → Define reusable contexts that attach to events
- **Design decisions** → Framework for event properties vs entities
- **Naming conventions** → `object_action` pattern (e.g., `product_viewed`, `cart_abandoned`)
- **Validation** → Use `scripts/validate_schema.py` before registering
- **Versioning** → Follow `MODEL-REVISION-ADDITION` semantic versioning

## Core Principles

1. **Business-driven design** - Schemas represent business concepts, not technical implementations
2. **Reusable entities** - Extract common properties into entity schemas used across events
3. **Modularity first** - Prefer entities over event properties for reusable data
4. **Validate everything** - All properties should have appropriate constraints
5. **Plan for evolution** - Design schemas expecting future additions
6. **Balance abstraction** - Find the right level between specific and generic schemas

## Design Decision Framework

### Event Property vs Entity Property

**Key Question**: Should this property live in the event schema or in an entity?

**Use Entity When:**
- Property describes a business object (user, product, game, banner, campaign)
- Property will be reused across multiple event types
- Property represents attributes of something that exists independently
- You need centralized control of property definitions
- Multiple teams will track the same conceptual object

**Use Event Property When:**
- Property is truly specific to the action itself
- Property only makes sense in context of this exact event
- Property won't be needed on other events

**Example - Module Interaction:**
```javascript
// GOOD: Entity for module, property for interaction type
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/module_interaction/jsonschema/1-0-0',
    data: {
      interaction_type: 'click',        // Event property - specific to action
      timestamp: '2024-01-15T10:30:00Z'
    }
  },
  context: [{
    schema: 'iglu:com.company/module/jsonschema/1-0-0',
    data: {
      module_id: 'promo-hero-001',      // Entity - describes the module
      module_type: 'promotional',
      position: 'homepage-hero',
      campaign_id: 'summer-sale-2024'
    }
  }]
});

// BAD: Everything in event properties
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/module_click/jsonschema/1-0-0',
    data: {
      interaction_type: 'click',
      module_id: 'promo-hero-001',      // Will be duplicated across events
      module_type: 'promotional',       // Same properties defined
      position: 'homepage-hero',        // differently on impression, scroll, etc.
      campaign_id: 'summer-sale-2024'
    }
  }
});
```

**Why Entities Win:**
1. **Consistency** - Module properties defined once, used everywhere
2. **Analysis** - Easy to query "show all events for promotional modules"
3. **Updates** - Change module schema once, affects all events
4. **Discovery** - Analysts know where to find module data

### Schema Abstraction Spectrum

Schemas exist on a spectrum from very specific to very generic:

```
Specific                                    Generic
|-----------------------------------------------|
button_clicked     ui_interaction     interaction
product_viewed     element_viewed     event
form_submitted     action_completed   activity
```

**Very Specific (Left Side):**
- **Pros**: Self-documenting, explicit, strong validation
- **Cons**: Schema proliferation, column explosion, maintenance overhead
- **Use for**: Core business events, regulated events, KPI events

**Very Generic (Right Side):**
- **Pros**: Fast implementation, minimal schemas, flexible
- **Cons**: Weak validation, analysis confusion, data quality issues
- **Use for**: Exploratory tracking, temporary experiments, low-value events

**Recommended Middle Ground:**
- Moderately generic event schemas (e.g., `ui_interaction`, `content_interaction`)
- Specific entities to add context (e.g., `button`, `video`, `product`)
- Use Data Products to apply specificity via Event Specs

**Example - Multi-Purpose Interaction Event:**
```json
// Event schema: ui_interaction (generic)
{
  "name": "ui_interaction",
  "properties": {
    "interaction_type": {
      "enum": ["impression", "click", "scroll", "expand", "dismiss"]
    }
  }
}

// Different entities provide context:
// 1. Button interaction + button entity
// 2. Video interaction + video entity  
// 3. Carousel interaction + carousel entity
```

### Global Contexts

Use global contexts to automatically attach entities to all events on a page/screen.

**When to Use:**
- Page/screen metadata needed on every event
- User properties that don't change during session
- Environment properties (platform, app version)
- Event categorization

**Implementation:**
```javascript
// Set once on page load
snowplow('addGlobalContexts', [{
  schema: 'iglu:com.company/page_context/jsonschema/1-0-0',
  data: {
    page_type: 'casino',
    vertical: 'slots',
    event_category: 'gameplay'
  }
}]);

// Now every event automatically gets page_context
snowplow('trackSelfDescribingEvent', {...});  // Has page_context
snowplow('trackPageView');                     // Has page_context
snowplow('trackStructEvent', {...});           // Has page_context
```

**Context Generators (Dynamic):**
```javascript
// Context changes based on conditions
snowplow('addGlobalContexts', [{
  // Function returns context dynamically
  contextGenerator: function() {
    return {
      schema: 'iglu:com.company/user/jsonschema/1-0-0',
      data: {
        user_id: getCurrentUserId(),              // Runtime value
        balance: getUserBalance(),                // Updates dynamically
        tier: getUserTier()
      }
    };
  }
}]);

// With conditional logic
snowplow('addGlobalContexts', [{
  filter: {
    allowlist: ['page_view', 'link_click']  // Only these events
  },
  contextGenerator: function() {
    if (isLoggedIn()) {
      return { schema: '...', data: {...} };
    }
    return null;  // Don't add context if not logged in
  }
}]);
```

### Avoiding Redundant Properties

**Don't duplicate tracker auto-captured data:**

The JavaScript tracker automatically captures:
- `page_url`, `page_urlhost`, `page_urlpath`
- `page_title`
- `page_referrer`
- `user_agent`
- `viewport_width`, `viewport_height`
- `doc_width`, `doc_height`

**BAD - Redundant:**
```json
{
  "name": "page_context",
  "properties": {
    "url": {},        // Already in page_url
    "hostname": {},   // Already in page_urlhost
    "path": {},       // Already in page_urlpath
    "title": {}       // Already in page_title
  }
}
```

**GOOD - Business context only:**
```json
{
  "name": "page_context",
  "properties": {
    "page_type": {"enum": ["casino", "sports", "poker"]},
    "vertical": {},
    "site_version": {},
    "ab_test_variant": {},
    "user_balance": {}
  }
}
```

**Why avoid duplication:**
1. **Confusion** - Two columns claiming same data, which is correct?
2. **Inconsistency** - Race conditions can cause mismatches
3. **Overhead** - Extra processing for no benefit
4. **Data models** - Snowplow models expect standard columns

## Event Schema Structure

Events describe "things that happened" using the `object_action` naming pattern.

### Template

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.yourcompany",
    "name": "object_action",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "property_name": {
      "type": "string",
      "description": "Clear description of what this represents",
      "maxLength": 500
    }
  },
  "required": ["property_name"],
  "additionalProperties": false
}
```

### Event Naming Patterns

**Good examples:**
- `product_viewed` - User viewed a product
- `form_submitted` - User completed form submission
- `video_played` - Video playback started
- `search_performed` - User executed search
- `experiment_viewed` - User exposed to A/B test

**Bad examples:**
- `click` - Too vague, what was clicked?
- `product` - Not an action
- `userViewedProduct` - Use snake_case, not camelCase
- `view_product` - Wrong order, use `product_viewed`

### Property Design Guidelines

**Include context-specific details:**
```json
{
  "product_id": {
    "type": "string",
    "description": "Unique product identifier",
    "pattern": "^[A-Z0-9-]+$",
    "maxLength": 50
  },
  "price": {
    "type": "number",
    "description": "Product price in currency units",
    "minimum": 0,
    "multipleOf": 0.01
  },
  "currency": {
    "type": "string",
    "description": "ISO 4217 currency code",
    "enum": ["USD", "EUR", "GBP", "CAD"]
  }
}
```

**Always use constraints:**
- `maxLength` on strings (typically 500, adjust per field)
- `minimum`/`maximum` on numbers
- `pattern` for format validation (IDs, emails, etc.)
- `enum` for known values
- `additionalProperties: false` to prevent undocumented fields

## Entity Schema Structure

Entities are reusable contexts describing "things" that exist independently.

### Single-Valued vs Multi-Valued Entities

**Single-valued**: One instance per event (e.g., one user, one page)
**Multi-valued**: Multiple instances per event (e.g., multiple products, multiple games)

**Example - Page View with Multiple Games Displayed:**
```javascript
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/page_view/jsonschema/1-0-0',
    data: { view_id: 'view-123' }
  },
  context: [
    // Single-valued: One user
    {
      schema: 'iglu:com.company/user/jsonschema/1-0-0',
      data: { user_id: 'user-456', tier: 'premium' }
    },
    // Single-valued: One page
    {
      schema: 'iglu:com.company/page/jsonschema/1-0-0',
      data: { page_type: 'casino', vertical: 'slots' }
    },
    // Multi-valued: Eight games displayed
    {
      schema: 'iglu:com.company/game/jsonschema/1-0-0',
      data: { game_id: 'game-001', name: 'Starburst', position: 1 }
    },
    {
      schema: 'iglu:com.company/game/jsonschema/1-0-0',
      data: { game_id: 'game-002', name: 'Gonzo\'s Quest', position: 2 }
    }
    // ... 6 more game entities
  ]
});
```

**Analysis implications:**
```sql
-- Single-valued: Simple join
SELECT 
  event_id,
  contexts_com_company_user_1.user_id,
  contexts_com_company_user_1.tier
FROM events

-- Multi-valued: Requires LATERAL FLATTEN or UNNEST
SELECT 
  event_id,
  game.value:game_id::string as game_id,
  game.value:position::int as position
FROM events,
LATERAL FLATTEN(input => contexts_com_company_game_1) as game
```

### Common Entity Types

**User identity:**
```json
{
  "self": {
    "vendor": "com.yourcompany",
    "name": "user",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "properties": {
    "user_id": { "type": "string", "maxLength": 50 },
    "account_type": { "type": "string", "enum": ["free", "premium", "enterprise"] },
    "signup_date": { "type": "string", "format": "date-time" }
  }
}
```

**Product:**
```json
{
  "self": {
    "vendor": "com.yourcompany",
    "name": "product",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "properties": {
    "product_id": { "type": "string", "maxLength": 50 },
    "name": { "type": "string", "maxLength": 200 },
    "category": { "type": "string", "maxLength": 100 },
    "price": { "type": "number", "minimum": 0 }
  }
}
```

**Content Module:**
```json
{
  "self": {
    "vendor": "com.yourcompany",
    "name": "content_module",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "properties": {
    "module_id": { "type": "string", "maxLength": 100 },
    "module_type": { 
      "type": "string", 
      "enum": ["carousel", "grid", "list", "featured"]
    },
    "content_type": {
      "type": "string",
      "enum": ["product", "article", "video", "promotion"]
    },
    "position": { "type": "string", "maxLength": 100 },
    "layout": { "type": "string", "maxLength": 50 }
  }
}
```

**Experiment:**
```json
{
  "self": {
    "vendor": "com.yourcompany",
    "name": "experiment",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "properties": {
    "experiment_id": { "type": "string", "maxLength": 100 },
    "variant": { "type": "string", "maxLength": 50 },
    "exposure_timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Entity Abstraction Levels

**Option 1: Specific Entities (Less Abstraction)**
```json
// Three separate schemas
navigation_menu_entity
product_carousel_entity  
featured_content_entity
```
**Pros**: Very explicit, type-safe
**Cons**: More schemas to maintain, less flexible

**Option 2: Generic Entity with Type (More Abstraction)**
```json
// One schema with type discriminator
{
  "name": "content_module",
  "properties": {
    "module_type": {"enum": ["navigation", "carousel", "featured"]},
    "module_id": {},
    "position": {}
  }
}
```
**Pros**: Fewer schemas, easier to extend
**Cons**: Less type safety, properties may not apply to all types

**Recommendation**: Use Option 2 (generic with type) unless:
- Different module types have completely different properties
- Strong type safety requirements
- Separate teams manage each type

## Schema Relationships

Events and entities work together to tell complete stories.

### Example: E-commerce Purchase Flow

**Events:**
- `product_viewed` - User saw product page
- `product_added_to_cart` - User added item to cart
- `checkout_started` - User began checkout
- `order_completed` - Purchase finalized

**Entities (attached to events):**
- `user` - Who performed the action
- `product` - What product was involved
- `cart` - Current cart state
- `experiment` - Any A/B tests active

**Event with entities:**
```javascript
trackSelfDescribingEvent({
  event: {
    schema: 'iglu:com.company/product_viewed/jsonschema/1-0-0',
    data: {
      view_timestamp: '2024-01-15T10:30:00Z',
      page_referrer: 'search'
    }
  },
  context: [
    {
      schema: 'iglu:com.company/product/jsonschema/1-0-0',
      data: {
        product_id: 'PROD-123',
        name: 'Blue Widget',
        price: 29.99,
        category: 'widgets'
      }
    },
    {
      schema: 'iglu:com.company/user/jsonschema/1-0-0',
      data: {
        user_id: 'user-456',
        account_type: 'premium'
      }
    }
  ]
});
```

## Versioning Strategy

Schema versions follow `MODEL-REVISION-ADDITION` format.

### When to Bump Each Component

**MODEL (1-x-x) - Breaking changes:**
- Remove required properties
- Change property types
- Make optional properties required
- Add stricter validation (narrower enums, smaller maxLength)
- Change property semantics

**REVISION (x-1-x) - Non-breaking additions:**
- Add optional properties
- Make required properties optional
- Loosen validation (wider enums, larger maxLength)
- Update descriptions (no code changes)

**ADDITION (x-x-1) - Documentation only:**
- Fix typos in descriptions
- Improve documentation clarity
- No schema structure changes

### Migration Planning

For breaking changes (MODEL bump):
1. Create new schema version
2. Update trackers to send both versions temporarily
3. Update data models to handle both versions
4. Deprecate old version after transition period
5. Remove old schema support

## Validation Workflow

Always validate schemas before registration.

### 1. Validate Syntax
```bash
python scripts/validate_schema.py your_schema.json
```

Checks:
- Valid JSON syntax
- Required Iglu fields present
- Proper version format
- JSONSchema compliance

### 2. Validate Business Logic

Manual review:
- Are property names clear and unambiguous?
- Do constraints match business rules?
- Are enums complete?
- Is the schema versioned correctly?

### 3. Test Event Generation
```bash
python scripts/test_event.py \
  --collector your-collector.com \
  --schema iglu:com.company/event/jsonschema/1-0-0 \
  --data '{"property": "value"}'
```

### 4. Register in Iglu

After validation, register schema in your Iglu repository (typically using Iglu CLI or API).

## Common Patterns

### Timestamp Properties
```json
{
  "event_timestamp": {
    "type": "string",
    "format": "date-time",
    "description": "ISO 8601 timestamp when event occurred"
  }
}
```

### Money Amounts
```json
{
  "amount": {
    "type": "number",
    "description": "Monetary amount in currency units",
    "minimum": 0,
    "multipleOf": 0.01
  },
  "currency": {
    "type": "string",
    "description": "ISO 4217 currency code",
    "enum": ["USD", "EUR", "GBP", "CAD"]
  }
}
```

### IDs with Validation
```json
{
  "order_id": {
    "type": "string",
    "description": "Unique order identifier",
    "pattern": "^ORD-[0-9]{6,10}$",
    "maxLength": 20
  }
}
```

### Duration Tracking
```json
{
  "duration_seconds": {
    "type": "integer",
    "description": "Duration in whole seconds",
    "minimum": 0,
    "maximum": 86400
  }
}
```

### Arrays of Items
```json
{
  "product_ids": {
    "type": "array",
    "description": "List of product identifiers",
    "items": {
      "type": "string",
      "maxLength": 50
    },
    "minItems": 1,
    "maxItems": 100
  }
}
```

## Practical Multi-Event Patterns

### Pattern 1: Generic Interaction Event + Specific Entities

**Use case**: Multiple similar interactions (impressions, clicks, scrolls) across different content modules.

**Design**:
```javascript
// One moderately generic event schema
{
  "name": "content_interaction",
  "properties": {
    "interaction_type": {
      "enum": ["impression", "click", "scroll", "expand", "dismiss"]
    }
  }
}

// Different entities provide context
// Product carousel
trackSelfDescribingEvent({
  event: { 
    schema: 'iglu:com.company/content_interaction/jsonschema/1-0-0',
    data: { interaction_type: 'click' }
  },
  context: [{
    schema: 'iglu:com.company/content_module/jsonschema/1-0-0',
    data: {
      module_id: 'product-carousel-001',
      module_type: 'carousel',
      content_type: 'product',
      position: 'homepage-hero'
    }
  }]
});

// Featured articles grid
trackSelfDescribingEvent({
  event: { 
    schema: 'iglu:com.company/content_interaction/jsonschema/1-0-0',
    data: { interaction_type: 'impression' }
  },
  context: [{
    schema: 'iglu:com.company/content_module/jsonschema/1-0-0',
    data: {
      module_id: 'featured-articles',
      module_type: 'grid',
      content_type: 'article',
      position: 'sidebar',
      is_personalized: true
    }
  }]
});

// Promotional banner
trackSelfDescribingEvent({
  event: { 
    schema: 'iglu:com.company/content_interaction/jsonschema/1-0-0',
    data: { interaction_type: 'click' }
  },
  context: [{
    schema: 'iglu:com.company/content_module/jsonschema/1-0-0',
    data: {
      module_id: 'summer-promo-2024',
      module_type: 'featured',
      content_type: 'promotion',
      campaign_id: 'summer-sale',
      position: 'header'
    }
  }]
});
```

**Benefits**:
- One event schema to maintain
- Easy to add new module types
- Consistent interaction tracking
- Filter by `module_type` or `content_type` for analysis

**Use Data Products** to organize:
```
Data Product: Product Carousel Interactions
  - Event Spec: Carousel Click (interaction_type = 'click', content_type = 'product')
  - Event Spec: Carousel Impression (interaction_type = 'impression', content_type = 'product')

Data Product: Article Content Interactions  
  - Event Spec: Article Click (interaction_type = 'click', content_type = 'article')
  - Event Spec: Article Impression (interaction_type = 'impression', content_type = 'article')
```

### Pattern 2: Event Categorization via Entity

**Use case**: Need to categorize all events (custom + out-of-box) for segmentation.

**Design**:
```javascript
// Event category entity
{
  "name": "event_category",
  "properties": {
    "category": {
      "enum": [
        "acquisition",
        "engagement", 
        "conversion",
        "retention",
        "support"
      ]
    },
    "subcategory": { "type": "string", "maxLength": 100 }
  }
}

// Add to custom events directly
trackSelfDescribingEvent({
  event: { schema: '...', data: {...} },
  context: [{
    schema: 'iglu:com.company/event_category/jsonschema/1-0-0',
    data: { 
      category: 'engagement',
      subcategory: 'content_interaction'
    }
  }]
});

// Add to page views via global context
snowplow('addGlobalContexts', [{
  schema: 'iglu:com.company/event_category/jsonschema/1-0-0',
  data: { 
    category: 'acquisition',
    subcategory: 'landing_page'
  }
}]);

snowplow('trackPageView');  // Now has event_category
```

**Analysis**:
```sql
-- All engagement events
SELECT *
FROM events
WHERE contexts_com_company_event_category_1.category = 'engagement'

-- Cluster table on category for performance (Databricks)
ALTER TABLE events
CLUSTER BY (contexts_com_company_event_category_1.category)
```

### Pattern 3: Page/Environment Context via Global Context

**Use case**: Every event needs page/environment metadata.

**Design**:
```javascript
// Page context entity
{
  "name": "page_context",
  "properties": {
    "page_type": { "enum": ["home", "product", "category", "checkout", "account"] },
    "site_section": { "type": "string", "maxLength": 100 },
    "content_category": { "type": "string", "maxLength": 100 },
    "ab_tests": {
      "type": "array",
      "items": { "type": "string", "maxLength": 100 }
    }
  }
}

// Set once on page load
function initializeTracking() {
  // Determine page type from URL or app state
  const pageType = determinePageType(window.location.pathname);
  
  snowplow('addGlobalContexts', [{
    schema: 'iglu:com.company/page_context/jsonschema/1-0-0',
    data: {
      page_type: pageType,
      site_section: getSiteSection(),
      content_category: getContentCategory(),
      ab_tests: getActiveTests()
    }
  }]);
}

// Now all events automatically get page_context
snowplow('trackPageView');
snowplow('trackSelfDescribingEvent', {...});
snowplow('trackStructEvent', {...});
```

**Benefits**:
- No need to pass page context to every tracking call
- Consistency across all events
- Easy to filter: "show all product page events"

### Pattern 4: Dynamic User Context

**Use case**: User properties that change during session (balance, tier).

**Design**:
```javascript
// User context with context generator
snowplow('addGlobalContexts', [{
  contextGenerator: function() {
    // Only add if user is logged in
    if (!isLoggedIn()) return null;
    
    return {
      schema: 'iglu:com.company/user/jsonschema/1-0-0',
      data: {
        user_id: getUserId(),
        tier: getUserTier(),           // May change during session
        balance: getCurrentBalance(),  // Updates after deposits/bets
        active_bonuses: getActiveBonuses()
      }
    };
  }
}]);

// Context automatically updates with latest values
placeBet();  // Balance decreases, context reflects new value
deposit();   // Balance increases, context reflects new value
```

### Pattern 5: Conditional Entities

**Use case**: Only attach entities when relevant.

**Design**:
```javascript
snowplow('addGlobalContexts', [
  {
    // Only add to specific events
    filter: {
      allowlist: ['content_interaction', 'product_view']
    },
    contextGenerator: function() {
      return {
        schema: 'iglu:com.company/recommendation/jsonschema/1-0-0',
        data: {
          model_version: 'v2.1',
          recommendation_source: 'collaborative-filtering'
        }
      };
    }
  },
  {
    // Add to all events if condition met
    contextGenerator: function() {
      // Only add during special promotions
      if (isSpecialPromotionActive()) {
        return {
          schema: 'iglu:com.company/promotion/jsonschema/1-0-0',
          data: {
            promotion_id: getCurrentPromotionId(),
            promotion_type: 'limited_time_offer'
          }
        };
      }
      return null;
    }
  }
]);
```

## Anti-Patterns to Avoid

**Don't use overly generic schemas:**
```json
// BAD - Too generic
{
  "name": "action",
  "properties": {
    "type": { "type": "string" },
    "data": { "type": "object" }
  }
}
```

**Don't mix concerns in one event:**
```json
// BAD - Mixing product view and cart state
{
  "name": "product_viewed",
  "properties": {
    "product_id": { "type": "string" },
    "cart_total": { "type": "number" },  // Belongs in cart entity
    "user_tier": { "type": "string" }    // Belongs in user entity
  }
}
```

**Don't skip validation constraints:**
```json
// BAD - No constraints
{
  "email": { "type": "string" }
}

// GOOD - Proper validation
{
  "email": {
    "type": "string",
    "format": "email",
    "maxLength": 320
  }
}
```

**Don't use technical names:**
```json
// BAD - Technical jargon
{ "name": "btn_click_evt" }

// GOOD - Clear business language
{ "name": "button_clicked" }
```

## Schema Design Checklist

Before finalizing a schema:

**Structure & Naming:**
- [ ] Name follows `object_action` pattern (events) or clear noun (entities)
- [ ] Decided event property vs entity property appropriately
- [ ] Chosen correct abstraction level (not too specific, not too generic)
- [ ] All properties have descriptions
- [ ] All properties have appropriate type constraints

**Validation:**
- [ ] String properties have `maxLength`
- [ ] Numbers have `minimum` and/or `maximum` where applicable
- [ ] Enums are used for fixed value sets
- [ ] `additionalProperties` is set to `false`
- [ ] Required properties are identified

**Reusability:**
- [ ] Properties that could be reused extracted to entities
- [ ] Single-valued vs multi-valued entity usage documented
- [ ] No redundant tracker auto-captured properties (URL, title, etc.)
- [ ] Considered global context for page/user properties

**Versioning:**
- [ ] Version follows semantic versioning rules
- [ ] Breaking changes properly planned with migration strategy

**Testing:**
- [ ] Schema validated with `validate_schema.py`
- [ ] Test event successfully sent with `test_event.py`
- [ ] Event + entity combination tested in target environment

**Organization:**
- [ ] Considered Data Products for organizing event specs
- [ ] Event categorization strategy defined (if needed)
- [ ] Documentation includes implementation examples

## Resources

**Schema validation:** Use `scripts/validate_schema.py`
**Event testing:** Use `scripts/test_event.py`
**Reference examples:** See `references/schema_examples.md`