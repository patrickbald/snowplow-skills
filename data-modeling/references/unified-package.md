# Snowplow Unified Digital Package Reference

Complete configuration and usage guide for the `snowplow_unified` dbt package.

## Package Overview

The Unified Digital package processes web and mobile event data into derived tables at varying aggregation levels. It supersedes the legacy `snowplow_web` and `snowpow_mobile` packages.

**Key features:**
- Cross-platform event processing (web + mobile)
- User identity stitching across devices
- Incremental processing with automatic deduplication
- Modular optional features (conversions, consent, web vitals)
- Support for custom entities and self-describing events

## Complete Variable Reference

### Database & Schema Configuration

```yaml
vars:
  snowplow_unified:
    # Required
    snowplow__atomic_schema: 'atomic'                # Schema with events table
    snowplow__database: 'analytics'                  # Target database
    snowplow__events_table: 'events'                 # Events table name
    
    # Target environment
    snowplow__dev_target_name: 'dev'                 # Name of dev target
    
    # Databricks specific
    snowplow__databricks_catalog: 'hive_metastore'   # Unity Catalog name
```

### Time Configuration

```yaml
vars:
  snowplow_unified:
    # Data boundaries
    snowplow__start_date: '2024-01-01'               # First event date
    
    # Incremental processing
    snowplow__backfill_limit_days: 30                # Max days per run
    snowplow__days_late_allowed: 3                   # Late data window
    snowplow__max_session_days: 3                    # Max session length
    snowplow__upsert_lookback_days: 30               # Update window
    
    # Session configuration
    snowplow__session_lookback_days: 365             # Session history depth
    snowplow__session_timestamp: 'collector_tstamp'  # Partition column
```

### Identifier Configuration

```yaml
vars:
  snowplow_unified:
    # Session identifiers (priority order)
    snowplow__session_identifiers:
      - domain_sessionid                             # Default
      - session_id                                   # Alternative
    
    # User identifiers (priority order)
    snowplow__user_identifiers:
      - user_id                                      # Authenticated (highest priority)
      - domain_userid                                # Cookie ID
      - network_userid                               # Collector ID (lowest priority)
    
    # User stitching
    snowplow__user_stitching_enabled: true           # Enable cross-device stitching
```

### Platform & App Filtering

```yaml
vars:
  snowplow_unified:
    # Platform enablement
    snowplow__enable_mobile: true                    # Process mobile events
    snowplow__enable_web: true                       # Process web events
    
    # App filtering
    snowplow__app_ids: []                            # Empty = all apps
    # snowplow__app_ids: ['app1', 'app2']           # Or specific apps
```

### Derived Context Enrichments

```yaml
vars:
  snowplow_unified:
    # Standard enrichments
    snowplow__enable_iab: true                       # IAB bot detection
    snowplow__enable_ua: true                        # User agent parsing
    snowplow__enable_yauaa: true                     # Device detection
```

### Optional Modules

```yaml
vars:
  snowplow_unified:
    # Conversion tracking
    snowplow__enable_conversions: false              # Standalone conversions table
    snowplow__conversion_events: []                  # Conversion definitions (see below)
    snowplow__conversion_path_source: 'sessions'     # 'sessions' or 'views'
    snowplow__conversion_path_lookback_days: 30
    snowplow__conversion_path_lookback_steps: 10
    
    # Consent tracking
    snowplow__enable_consent: false                  # Consent module
    snowplow__consent_event_name: 'consent_preferences'
    
    # Core Web Vitals (web only)
    snowplow__enable_cwv: false                      # Performance metrics
    snowplow__cwv_percentile: 75                     # Measurement percentile
    
    # Application errors
    snowplow__enable_app_errors: false               # Error tracking
```

### Web-Specific Configuration

```yaml
vars:
  snowplow_unified:
    # Page ping configuration (must match tracker settings)
    snowplow__min_visit_length: 5                    # Seconds before first ping
    snowplow__heartbeat: 10                          # Seconds between pings
    
    # Page view tracking
    snowplow__total_all_conversions: false           # Sum all conversion values
```

### Custom Entities & SDEs (Redshift/Postgres)

```yaml
vars:
  snowplow_unified:
    snowplow__entities_or_sdes:
      # Single-valued entity (one per event)
      - schema: 'contexts_com_company_user_1'
        prefix: 'user'
        alias: 'cu'
        single_entity: true
      
      # Multi-valued entity (array - requires custom models)
      - schema: 'contexts_com_company_product_1'
        prefix: 'product'
        alias: 'cp'
        single_entity: false
```

### Performance & Processing

```yaml
vars:
  snowplow_unified:
    # Processing limits
    snowplow__limit_page_views_to_session: true      # Session-level page view limit
    
    # Materialization strategy
    snowplow__incremental_materialization: 'snowplow_incremental'
    
    # BigQuery specific
    snowplow__derived_tstamp_partitioned: true       # Use derived_tstamp for partitioning
```

## Conversion Configuration

Conversion events add metrics to the sessions table or create a standalone conversions table.

### Basic Conversion

```yaml
vars:
  snowplow_unified:
    snowplow__conversion_events:
      - name: 'purchase'
        condition: "event_name = 'order_completed'"
        value: "unstruct_event_com_company_order_1:total::number"
        default_value: 0
        list_events: false
```

Creates columns in sessions table:
- `cv_purchase` - Count of purchases
- `cv_purchase_value` - Sum of purchase values  
- `cv_purchase_tstamp` - First purchase timestamp

### Conversion with Event List

```yaml
vars:
  snowplow_unified:
    snowplow__conversion_events:
      - name: 'add_to_cart'
        condition: "event_name = 'product_added'"
        list_events: true
```

Creates columns:
- `cv_add_to_cart` - Count of add to carts
- `cv_add_to_cart_tstamp` - First add timestamp
- `cv_add_to_cart_id` - First event ID
- `cv_add_to_cart_ids` - Array of all event IDs
- `cv_add_to_cart_tstamp_last` - Last add timestamp

### Multiple Conversions

```yaml
vars:
  snowplow_unified:
    snowplow__conversion_events:
      - name: 'purchase'
        condition: "event_name = 'order_completed'"
        value: "unstruct_event_com_company_order_1:total::number"
      
      - name: 'signup'
        condition: "event_name = 'user_registered'"
        list_events: true
      
      - name: 'trial_start'
        condition: "event_name = 'trial_started' and contexts_com_company_user_1_cu:account_type = 'premium'"
```

## Schema Configuration

Customize target schemas:

```yaml
models:
  snowplow_unified:
    # Manifest tables
    base:
      manifest:
        +schema: custom_manifest
    
    # Scratch/staging tables
    base:
      scratch:
        +schema: custom_scratch
    sessions:
      scratch:
        +schema: custom_scratch
    users:
      scratch:
        +schema: custom_scratch
    views:
      scratch:
        +schema: custom_scratch
    
    # Derived tables
    sessions:
      +schema: custom_derived
    users:
      +schema: custom_derived
    views:
      +schema: custom_derived
    user_mapping:
      +schema: custom_derived
    
    # Seeds
seeds:
  snowplow_unified:
    +schema: custom_seeds
```

## Model Outputs

### snowplow_unified_events_this_run

Foundation table for each run containing:
- All events to be processed
- Deduplicated
- Resolved user/session identifiers
- All atomic columns
- Custom entity/SDE fields (if configured)

### snowplow_unified_views

One row per page/screen view:
```sql
view_id                      -- Unique identifier
session_identifier           -- Parent session
user_identifier             -- Resolved user
view_start_tstamp           -- Start time
view_end_tstamp             -- End time
engaged_time_s              -- Active time
absolute_time_s             -- Total time

-- Web
page_url
page_title
page_referrer
page_urlscheme
page_urlhost
page_urlpath
vertical_pixels_scrolled
horizontal_pixels_scrolled
doc_width
doc_height

-- Mobile
screen_name
screen_type

-- Device
device_family
os_family
os_name
os_version
browser_name
browser_version

-- Geo
geo_country
geo_region
geo_city
geo_zipcode
geo_latitude
geo_longitude
```

### snowplow_unified_sessions

One row per session:
```sql
session_identifier
user_identifier
session_start_tstamp
session_end_tstamp
session_duration_s
engaged_time_s
absolute_time_s
page_views
views

-- Engagement
vertical_pixels_scrolled_max
horizontal_pixels_scrolled_max

-- First/last page
first_page_url
first_page_title
last_page_url
last_page_title

-- Marketing
refr_source
refr_medium
refr_term
refr_urlhost
refr_urlpath
mkt_source
mkt_medium
mkt_campaign
mkt_term
mkt_content
mkt_clickid
mkt_network

-- Device (first in session)
device_family
os_family
os_name
os_version
os_timezone
browser_name
browser_version
browser_language

-- Geo (first in session)
geo_country
geo_region
geo_city
geo_zipcode
geo_latitude
geo_longitude
geo_region_name
geo_timezone

-- Platform
platform
app_id

-- Conversion columns (if configured)
cv_{conversion_name}
cv_{conversion_name}_value
cv_{conversion_name}_tstamp
-- etc.
```

### snowplow_unified_users

One row per user:
```sql
user_identifier
user_id                      -- Authenticated (if available)
domain_userid                -- Cookie
network_userid               -- Collector

-- Lifecycle
first_session_start
last_session_start
session_count
engaged_time_s
absolute_time_s
page_views
views

-- First/last pages
first_page_url
first_page_title
last_page_url
last_page_title

-- Devices
device_count
platform_mix                 -- Platforms used

-- Marketing (first/last)
first_refr_source
first_refr_medium
last_refr_source
last_refr_medium
```

### snowplow_unified_user_mapping

Identity graph:
```sql
user_identifier             -- Canonical user ID
other_user_id               -- Linked identifier
other_user_id_type          -- Type: user_id, domain_userid, network_userid
```

Example:
```
user_identifier | other_user_id    | other_user_id_type
----------------|------------------|-------------------
user-123        | auth-456         | user_id
user-123        | cookie-789       | domain_userid  
user-123        | network-012      | network_userid
```

### Optional: snowplow_unified_conversions

If `snowplow__enable_conversions: true`:
```sql
event_id
event_name
event_in_session_index
session_identifier
user_identifier
cv_tstamp                   -- Conversion timestamp
cv_type                     -- Conversion name
cv_value                    -- Conversion value

-- Web
page_url
page_referrer

-- Mobile
screen_name
screen_type

-- Attribution
refr_source
refr_medium
mkt_source
mkt_medium
mkt_campaign
```

## Usage Patterns

### Enable Specific Enrichments

```yaml
vars:
  snowplow_unified:
    snowplow__enable_iab: true
    snowplow__enable_yauaa: true
    snowplow__enable_ua: false    # Disable if not needed
```

### Web-Only Implementation

```yaml
vars:
  snowplow_unified:
    snowplow__enable_web: true
    snowplow__enable_mobile: false
```

### Mobile-Only Implementation

```yaml
vars:
  snowplow_unified:
    snowplow__enable_web: false
    snowplow__enable_mobile: true
```

### Filter by App IDs

```yaml
vars:
  snowplow_unified:
    snowplow__app_ids: ['ios-app', 'android-app']
```

### Aggressive Performance Mode (Dev)

```yaml
vars:
  snowplow_unified:
    snowplow__backfill_limit_days: 1
    snowplow__upsert_lookback_days: 1
    snowplow__session_lookback_days: 30
    snowplow__max_session_days: 1
```

### Conservative Performance Mode (Prod)

```yaml
vars:
  snowplow_unified:
    snowplow__backfill_limit_days: 30
    snowplow__upsert_lookback_days: 30
    snowplow__session_lookback_days: 365
    snowplow__max_session_days: 3
```

## Best Practices

1. **Always specify `snowplow__start_date`** - Set to first event date
2. **Use environment-specific configs** - Smaller backfill for dev
3. **Enable only needed enrichments** - Reduce processing overhead
4. **Configure custom entities carefully** - Only single-valued in `entities_or_sdes`
5. **Test conversion definitions** - Verify SQL conditions work
6. **Monitor manifest table** - Check processing is advancing
7. **Use selectors for runs** - `--selector snowplow_unified`
8. **Full-refresh sparingly** - Use `dbt run --full-refresh` only when needed