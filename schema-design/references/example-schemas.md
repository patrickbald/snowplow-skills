# Snowplow Schema Examples

Complete, production-ready schema examples for common use cases.

## Table of Contents

- [E-commerce Schemas](#e-commerce-schemas)
- [Media & Content Schemas](#media--content-schemas)
- [Form & Interaction Schemas](#form--interaction-schemas)
- [Experimentation Schemas](#experimentation-schemas)
- [Identity & User Schemas](#identity--user-schemas)

## E-commerce Schemas

### Product Viewed Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "product_viewed",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "view_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When product was viewed"
    },
    "page_referrer": {
      "type": "string",
      "enum": ["search", "category", "recommendation", "direct", "external"],
      "description": "How user arrived at product page"
    },
    "position_in_list": {
      "type": "integer",
      "description": "Position in search/category results (if applicable)",
      "minimum": 1,
      "maximum": 1000
    }
  },
  "required": ["view_timestamp"],
  "additionalProperties": false
}
```

### Product Entity

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "product",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "product_id": {
      "type": "string",
      "description": "Unique product identifier",
      "pattern": "^[A-Z0-9-]+$",
      "maxLength": 50
    },
    "name": {
      "type": "string",
      "description": "Product name",
      "maxLength": 200
    },
    "category": {
      "type": "string",
      "description": "Product category",
      "maxLength": 100
    },
    "subcategory": {
      "type": "string",
      "description": "Product subcategory",
      "maxLength": 100
    },
    "brand": {
      "type": "string",
      "description": "Product brand",
      "maxLength": 100
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
      "enum": ["USD", "EUR", "GBP", "CAD", "AUD"]
    },
    "inventory_status": {
      "type": "string",
      "description": "Current inventory availability",
      "enum": ["in_stock", "low_stock", "out_of_stock", "backorder"]
    }
  },
  "required": ["product_id", "name", "price", "currency"],
  "additionalProperties": false
}
```

### Cart Updated Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "cart_updated",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "description": "Type of cart update",
      "enum": ["add", "remove", "update_quantity", "clear"]
    },
    "quantity_change": {
      "type": "integer",
      "description": "Change in quantity (positive for add, negative for remove)"
    },
    "cart_total": {
      "type": "number",
      "description": "Total cart value after update",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "cart_item_count": {
      "type": "integer",
      "description": "Total items in cart after update",
      "minimum": 0
    },
    "currency": {
      "type": "string",
      "description": "ISO 4217 currency code",
      "enum": ["USD", "EUR", "GBP", "CAD", "AUD"]
    }
  },
  "required": ["action", "cart_total", "cart_item_count", "currency"],
  "additionalProperties": false
}
```

### Order Completed Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "order_completed",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "order_id": {
      "type": "string",
      "description": "Unique order identifier",
      "pattern": "^ORD-[0-9]{6,10}$",
      "maxLength": 20
    },
    "total_amount": {
      "type": "number",
      "description": "Total order amount",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "tax_amount": {
      "type": "number",
      "description": "Tax amount",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "shipping_amount": {
      "type": "number",
      "description": "Shipping cost",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "discount_amount": {
      "type": "number",
      "description": "Total discount applied",
      "minimum": 0,
      "multipleOf": 0.01
    },
    "currency": {
      "type": "string",
      "description": "ISO 4217 currency code",
      "enum": ["USD", "EUR", "GBP", "CAD", "AUD"]
    },
    "payment_method": {
      "type": "string",
      "description": "Payment method used",
      "enum": ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay", "bank_transfer", "other"]
    },
    "item_count": {
      "type": "integer",
      "description": "Number of items in order",
      "minimum": 1
    },
    "is_first_purchase": {
      "type": "boolean",
      "description": "Whether this is customer's first purchase"
    }
  },
  "required": ["order_id", "total_amount", "currency", "payment_method", "item_count"],
  "additionalProperties": false
}
```

## Media & Content Schemas

### Video Started Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "video_started",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "video_id": {
      "type": "string",
      "description": "Unique video identifier",
      "maxLength": 100
    },
    "video_title": {
      "type": "string",
      "description": "Video title",
      "maxLength": 200
    },
    "duration_seconds": {
      "type": "integer",
      "description": "Total video duration",
      "minimum": 0
    },
    "quality": {
      "type": "string",
      "description": "Playback quality",
      "enum": ["auto", "240p", "360p", "480p", "720p", "1080p", "1440p", "4k"]
    },
    "is_autoplay": {
      "type": "boolean",
      "description": "Whether video started via autoplay"
    }
  },
  "required": ["video_id", "video_title", "duration_seconds"],
  "additionalProperties": false
}
```

### Article Read Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "article_read",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "article_id": {
      "type": "string",
      "description": "Unique article identifier",
      "maxLength": 100
    },
    "word_count": {
      "type": "integer",
      "description": "Article word count",
      "minimum": 0
    },
    "percent_read": {
      "type": "integer",
      "description": "Percentage of article read",
      "minimum": 0,
      "maximum": 100
    },
    "time_spent_seconds": {
      "type": "integer",
      "description": "Time spent reading in seconds",
      "minimum": 0
    },
    "category": {
      "type": "string",
      "description": "Article category",
      "maxLength": 100
    }
  },
  "required": ["article_id", "percent_read", "time_spent_seconds"],
  "additionalProperties": false
}
```

## Form & Interaction Schemas

### Form Started Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "form_started",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "form_id": {
      "type": "string",
      "description": "Unique form identifier",
      "maxLength": 100
    },
    "form_name": {
      "type": "string",
      "description": "Human-readable form name",
      "maxLength": 200
    },
    "form_type": {
      "type": "string",
      "description": "Type of form",
      "enum": ["signup", "contact", "checkout", "survey", "login", "search", "other"]
    },
    "total_fields": {
      "type": "integer",
      "description": "Total number of fields in form",
      "minimum": 1
    }
  },
  "required": ["form_id", "form_type", "total_fields"],
  "additionalProperties": false
}
```

### Form Submitted Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "form_submitted",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "form_id": {
      "type": "string",
      "description": "Unique form identifier",
      "maxLength": 100
    },
    "fields_completed": {
      "type": "integer",
      "description": "Number of fields filled",
      "minimum": 0
    },
    "fields_with_errors": {
      "type": "integer",
      "description": "Number of fields with validation errors",
      "minimum": 0
    },
    "time_to_complete_seconds": {
      "type": "integer",
      "description": "Time from start to submit",
      "minimum": 0
    },
    "submission_success": {
      "type": "boolean",
      "description": "Whether submission succeeded"
    }
  },
  "required": ["form_id", "fields_completed", "time_to_complete_seconds", "submission_success"],
  "additionalProperties": false
}
```

### Search Performed Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "search_performed",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "search_query": {
      "type": "string",
      "description": "User's search query",
      "maxLength": 500
    },
    "results_count": {
      "type": "integer",
      "description": "Number of results returned",
      "minimum": 0
    },
    "search_type": {
      "type": "string",
      "description": "Type of search performed",
      "enum": ["product", "content", "site", "help", "other"]
    },
    "filters_applied": {
      "type": "array",
      "description": "List of filters applied",
      "items": {
        "type": "string",
        "maxLength": 100
      },
      "maxItems": 20
    }
  },
  "required": ["search_query", "results_count", "search_type"],
  "additionalProperties": false
}
```

## Experimentation Schemas

### Experiment Viewed Event

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "experiment_viewed",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "experiment_id": {
      "type": "string",
      "description": "Unique experiment identifier",
      "maxLength": 100
    },
    "experiment_name": {
      "type": "string",
      "description": "Human-readable experiment name",
      "maxLength": 200
    },
    "variant": {
      "type": "string",
      "description": "Assigned variant",
      "maxLength": 50
    },
    "exposure_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When user was exposed to experiment"
    }
  },
  "required": ["experiment_id", "variant", "exposure_timestamp"],
  "additionalProperties": false
}
```

### Experiment Entity

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "experiment",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "experiment_id": {
      "type": "string",
      "description": "Unique experiment identifier",
      "maxLength": 100
    },
    "variant": {
      "type": "string",
      "description": "User's assigned variant",
      "maxLength": 50
    },
    "assignment_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When variant was assigned"
    }
  },
  "required": ["experiment_id", "variant"],
  "additionalProperties": false
}
```

## Identity & User Schemas

### User Entity

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "user",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Internal user identifier",
      "maxLength": 50
    },
    "account_type": {
      "type": "string",
      "description": "User account type",
      "enum": ["free", "trial", "premium", "enterprise"]
    },
    "signup_date": {
      "type": "string",
      "format": "date-time",
      "description": "When user signed up"
    },
    "subscription_status": {
      "type": "string",
      "description": "Current subscription status",
      "enum": ["active", "cancelled", "expired", "paused"]
    },
    "lifetime_value": {
      "type": "number",
      "description": "Total revenue from user",
      "minimum": 0,
      "multipleOf": 0.01
    }
  },
  "required": ["user_id", "account_type"],
  "additionalProperties": false
}
```

### Session Entity

```json
{
  "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
  "self": {
    "vendor": "com.company",
    "name": "session",
    "format": "jsonschema",
    "version": "1-0-0"
  },
  "type": "object",
  "properties": {
    "session_id": {
      "type": "string",
      "description": "Unique session identifier",
      "maxLength": 100
    },
    "session_start_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When session started"
    },
    "referrer_source": {
      "type": "string",
      "description": "Traffic source for session",
      "enum": ["direct", "organic_search", "paid_search", "social", "email", "referral", "other"]
    },
    "landing_page": {
      "type": "string",
      "description": "First page visited in session",
      "maxLength": 500
    }
  },
  "required": ["session_id", "session_start_timestamp"],
  "additionalProperties": false
}
```