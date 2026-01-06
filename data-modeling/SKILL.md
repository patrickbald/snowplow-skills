---
name: snowplow-dbt-modeling
description: Expert guidance for implementing Snowplow dbt data models including the Unified Digital package, custom model development, incremental processing strategies, entity modeling, conversion tracking, user stitching, and performance optimization. Use when implementing Snowplow dbt packages, creating custom behavioral data models, optimizing incremental models, configuring sessionization logic, modeling custom entities, or troubleshooting dbt model performance.
---

# Snowplow dbt Modeling

Comprehensive guidance for building production-ready Snowplow data models with dbt.

## Quick Reference

- **Unified Digital package** → Main package for web & mobile (see `references/unified_package.md`)
- **Package configuration** → Key variables and settings (see `references/configuration.md`)
- **Custom models** → Build on `_events_this_run` tables (see `references/custom_models.md`)
- **Performance tuning** → Optimize incremental processing (see `references/performance.md`)

## Core Concepts

### Snowplow dbt Packages

**Unified Digital** (`snowplow_unified`):
- Combines web and mobile tracking
- Produces views, sessions, users tables
- Supports consent, conversions, core web vitals
- Cross-platform user stitching

**E-commerce** (`snowplow_ecommerce`):
- Cart, checkout, transaction modeling
- Product interaction analysis

**Media Player** (`snowplow_media_player`):
- Video/audio playback statistics
- Engagement metrics

**Attribution** (`snowplow_attribution`):
- Multi-touch attribution modeling
- Campaign performance analysis

**Legacy packages** (superseded by Unified):
- Web (`snowplow_web`) - web-only
- Mobile (`snowplow_mobile`) - mobile-only

### Package Architecture

All packages follow this structure:

```
models/
├── base/              # Incremental logic, deduplication
│   └── snowplow_unified_base_events_this_run
├── views/             # Page/screen view aggregations
│   └── snowplow_unified_views
├── sessions/          # Session-level aggregations
│   └── snowplow_unified_sessions
├── users/             # User-level aggregations  
│   └── snowplow_unified_users
├── user_mapping/      # Identity stitching
│   └── snowplow_unified_user_mapping
└── optional/          # Conversions, consent, etc.
```

## Installation & Setup

### 1. Add Package Dependency

`packages.yml`:
```yaml
packages:
  - package: snowplow/snowplow_unified
    version: [">=1.0.0", "<2.0.0"]
```

Run:
```bash
dbt deps
```

### 2. Required Configuration

Minimum `dbt_project.yml`:
```yaml
vars:
  snowplow_unified:
    snowplow__atomic_schema: 'atomic'           # Schema containing events table
    snowplow__database: 'analytics'             # Target database
    snowplow__events_table: 'events'            # Events table name
    snowplow__start_date: '2024-01-01'         # First event date
```

### 3. Run Models

Copy `selectors.yml` from package to your project root, then:
```bash
# First time only - load seed data
dbt seed --select snowplow_unified --full-refresh

# Run models
dbt run --selector snowplow_unified

# Run tests
dbt test --selector snowplow_unified
```

## Core Configuration Variables

### Time Bounds

```yaml
vars:
  snowplow_unified:
    # Data processing window
    snowplow__start_date: '2024-01-01'
    snowplow__backfill_limit_days: 30           # Max days per run
    snowplow__days_late_allowed: 3              # Late-arriving data window
    snowplow__max_session_days: 3               # Max session duration
    snowplow__upsert_lookback_days: 30          # Update window
```

### Session Configuration

```yaml
vars:
  snowplow_unified:
    snowplow__session_lookback_days: 365        # Session history to check
    snowplow__session_inactivity_threshold: 30  # Minutes of inactivity = new session
    
    # Custom session identifier (default: domain_sessionid)
    snowplow__session_identifiers:
      - domain_sessionid
      - session_id
```

### User Configuration

```yaml
vars:
  snowplow_unified:
    # User ID resolution order (priority 1 to N)
    snowplow__user_identifiers:
      - user_id            # Authenticated user
      - domain_userid      # Cookie ID  
      - network_userid     # Collector ID
    
    snowplow__user_stitching_enabled: true     # Enable cross-device stitching
```

### Platform Tracking

```yaml
vars:
  snowplow_unified:
    snowplow__enable_mobile: true              # Process mobile events
    snowplow__enable_web: true                 # Process web events
    snowplow__app_ids: []                      # Empty = all apps, or ['app1', 'app2']
```

### Derived Contexts

```yaml
vars:
  snowplow_unified:
    snowplow__enable_iab: true                 # IAB bot detection
    snowplow__enable_ua: true                  # User agent parsing
    snowplow__enable_yauaa: true               # Device/browser detection
```

## Core Models

### Events This Run

**snowplow_unified_events_this_run**

Foundation table containing all events for current run:
- Deduplicated events
- Resolved user/session identifiers
- All atomic columns available
- Custom entity/SDE fields (if configured)

### Views Model

**snowplow_unified_views**

Page/screen view aggregations:
```sql
view_id                     -- Unique view identifier
session_identifier          -- Parent session
user_identifier            -- Resolved user
view_start_tstamp          -- View start time
view_end_tstamp            -- View end time
engaged_time_s             -- Active engagement time
absolute_time_s            -- Total time (includes inactive)

-- Web-specific
page_url
page_title
page_referrer
vertical_pixels_scrolled   -- Max scroll depth
horizontal_pixels_scrolled

-- Mobile-specific
screen_name
screen_type

-- Device
device_family
os_family
browser_name
```

### Sessions Model

**snowplow_unified_sessions**

Session-level aggregations:
```sql
session_identifier
user_identifier
session_start_tstamp
session_end_tstamp
session_duration_s
engaged_time_s             -- Sum of engaged time across views
absolute_time_s            -- Total session duration
page_views                 -- Count of page/screen views
views                      -- Alias for page_views

-- Engagement
vertical_pixels_scrolled_max
horizontal_pixels_scrolled_max

-- Marketing attribution
refr_source                -- Traffic source
refr_medium                -- Traffic medium
refr_term                  -- Search term
mkt_source                 -- Campaign source
mkt_medium                 -- Campaign medium
mkt_campaign               -- Campaign name

-- Device/browser
device_family
os_family
os_version
browser_name
browser_version

-- Geography
geo_country
geo_region
geo_city

-- Platform
platform                   -- web, mob, srv, etc.
app_id
```

### Users Model

**snowplow_unified_users**

User-level aggregations:
```sql
user_identifier            -- Resolved user ID
user_id                    -- Authenticated ID (if available)
domain_userid              -- Cookie ID
network_userid             -- Collector ID

-- Lifecycle
first_session_start        -- First ever session
last_session_start         -- Most recent session
session_count              -- Total sessions

-- Engagement
engaged_time_s             -- Total engaged time
absolute_time_s            -- Total time
page_views                 -- Total page/screen views
views                      -- Alias for page_views

-- Marketing
first_refr_source          -- First referrer
last_refr_source           -- Last referrer
```

### User Mapping

**snowplow_unified_user_mapping**

Identity graph for user stitching:
```sql
user_identifier            -- Resolved canonical user ID
other_user_id              -- Other identifier for this user
other_user_id_type         -- Type: user_id, domain_userid, network_userid
```

## Modeling Custom Entities & SDEs

### Configuration

For Redshift/Postgres, use `snowplow__entities_or_sdes`:
```yaml
vars:
  snowplow_unified:
    snowplow__entities_or_sdes:
      # Single entity (one per event)
      - schema: 'contexts_com_company_user_1'
        prefix: 'user'
        alias: 'cu'
        single_entity: true
      
      # Multi-valued entity (array)
      - schema: 'contexts_com_company_product_1'
        prefix: 'product'
        alias: 'cp'
        single_entity: false
```

**Important**: Only single-valued entities should be added to `events_this_run`. Multi-valued entities require custom models.

### Accessing in Custom Models

**Single entity:**
```sql
select
  event_id,
  contexts_com_company_user_1_cu.user_tier,
  contexts_com_company_user_1_cu.account_type
from {{ ref('snowplow_unified_events_this_run') }}
```

**Multi-valued entity:**
```sql
select
  event_id,
  prod.value:product_id::string as product_id,
  prod.value:price::number as price
from {{ ref('snowplow_unified_events_this_run') }},
lateral flatten(input => contexts_com_company_product_1) as prod
```

## Conversion Tracking

### Session-Level Conversions

Add conversion columns to sessions table:
```yaml
vars:
  snowplow_unified:
    snowplow__conversion_events:
      - name: 'purchase'
        condition: "event_name = 'order_completed'"
        value: "unstruct_event_com_company_order_1:total::number"
        default_value: 0
        list_events: false
      
      - name: 'signup'
        condition: "event_name = 'user_registered'"
        list_events: true
```

Creates columns in `snowplow_unified_sessions`:
- `cv_{name}` - Count of conversions
- `cv_{name}_value` - Sum of values
- `cv_{name}_tstamp` - First conversion timestamp
- `cv_{name}_id` - First conversion event_id (if list_events: true)
- `cv_{name}_ids` - Array of all conversion event_ids (if list_events: true)
- `cv_{name}_tstamp_last` - Last conversion timestamp (if list_events: true)

### Conversions Table (Optional)

Enable standalone conversions table:
```yaml
vars:
  snowplow_unified:
    snowplow__enable_conversions: true
    snowplow__conversion_events:  # Same as above
      - name: 'purchase'
        # ...
```

Creates `snowplow_unified_conversions` with one row per conversion event.

## Custom Model Development

### Pattern 1: Extend Derived Tables

Build on sessions/views/users:
```sql
-- models/custom/marketing_sessions.sql
{{
  config(
    materialized='incremental',
    unique_key='session_identifier',
    incremental_strategy='merge'
  )
}}

select
  s.*,
  
  -- Add custom logic
  case
    when s.mkt_medium = 'cpc' then 'paid'
    when s.refr_medium = 'search' then 'organic'
    else 'other'
  end as channel_type,
  
  -- User attributes from custom entity
  u.subscription_tier,
  u.account_created_date

from {{ ref('snowplow_unified_sessions') }} s
left join {{ ref('custom_user_attributes') }} u
  on s.user_identifier = u.user_identifier

{% if is_incremental() %}
where s.session_start_tstamp >= (
  select max(session_start_tstamp) from {{ this }}
)
{% endif %}
```

### Pattern 2: Custom Event Aggregation

Process custom SDEs from `events_this_run`:
```sql
-- models/custom/product_interactions.sql
{{
  config(
    materialized='incremental',
    unique_key='interaction_id'
  )
}}

select
  {{ dbt_utils.generate_surrogate_key(['event_id']) }} as interaction_id,
  collector_tstamp,
  session_identifier,
  user_identifier,
  
  -- Extract from unstruct event
  unstruct_event_com_company_product_interaction_1:product_id::string as product_id,
  unstruct_event_com_company_product_interaction_1:interaction_type::string as interaction_type,
  unstruct_event_com_company_product_interaction_1:duration_ms::integer as duration_ms

from {{ ref('snowplow_unified_events_this_run') }}
where event_name = 'product_interaction'

{% if is_incremental() %}
and collector_tstamp >= (
  select dateadd(day, -{{ var('snowplow__upsert_lookback_days', 30) }}, max(collector_tstamp))
  from {{ this }}
)
{% endif %}
```

### Pattern 3: Custom Sessionization

Override default session logic:
```sql
-- models/custom/engagement_sessions.sql
with events as (
  select
    *,
    lag(collector_tstamp) over (
      partition by user_identifier 
      order by collector_tstamp
    ) as prev_event_tstamp,
    
    -- Custom break: 5 minute inactivity OR page change
    case
      when datediff('minute', prev_event_tstamp, collector_tstamp) > 5
        or lag(page_url) over (partition by user_identifier order by collector_tstamp) != page_url
      then 1
      else 0
    end as new_session_flag
    
  from {{ ref('snowplow_unified_events_this_run') }}
),

session_groups as (
  select
    *,
    sum(new_session_flag) over (
      partition by user_identifier
      order by collector_tstamp
      rows between unbounded preceding and current row
    ) as session_group
  from events
)

select
  {{ dbt_utils.generate_surrogate_key(['user_identifier', 'session_group']) }} as custom_session_id,
  user_identifier,
  min(collector_tstamp) as session_start,
  max(collector_tstamp) as session_end,
  count(*) as event_count
from session_groups
group by 1, 2
```

## Performance Optimization

### 1. Limit Backfill Window

Reduce data processed per run:
```yaml
vars:
  snowplow_unified:
    snowplow__backfill_limit_days: 30   # Max 30 days per run
    snowplow__upsert_lookback_days: 30  # Look back 30 days for updates
```

Use environment-specific values:
```yaml
vars:
  snowplow_unified:
    snowplow__backfill_limit_days: "{{ 1 if target.name == 'dev' else 30 }}"
```

### 2. Optimize Session Lookback

Reduce if sessions are shorter:
```yaml
vars:
  snowplow_unified:
    snowplow__session_lookback_days: 90    # Down from default 365
    snowplow__max_session_days: 1          # Down from default 3
```

### 3. Table Configuration

**Partitioning:**
```yaml
# dbt_project.yml
models:
  snowplow_unified:
    sessions:
      +partition_by:
        field: session_start_tstamp
        data_type: timestamp
        granularity: day
```

**Clustering:**
```yaml
models:
  snowplow_unified:
    sessions:
      +cluster_by: ['user_identifier', 'session_start_tstamp']
```

### 4. Databricks Optimization

Enable auto-optimization:
```sql
ALTER TABLE snowplow_unified_derived.snowplow_unified_sessions
SET TBLPROPERTIES (
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true
)
```

Or in model config:
```yaml
models:
  snowplow_unified:
    sessions:
      +tblproperties:
        delta.autoOptimize.optimizeWrite: true
        delta.autoOptimize.autoCompact: true
```

## Incremental Processing & Manifests

### How It Works

1. **Manifest table** tracks processing state per model
2. Each run processes only new events since last run
3. **Lookback window** handles late-arriving data
4. **Session/user updates** via upsert strategy

### Manifest Table

**snowplow_unified_incremental_manifest**

Tracks processing state:
```sql
select * from snowplow_unified_snowplow_manifest.snowplow_unified_incremental_manifest

-- Columns:
model                  -- Model name
last_success          -- Last successful run timestamp
target_schema         -- Target schema name
```

### Resetting Models

**Full refresh (all models):**
```bash
dbt run --selector snowplow_unified --full-refresh
```

**Reset specific model:**
```sql
delete from snowplow_unified_snowplow_manifest.snowplow_unified_incremental_manifest
where model = 'snowplow_unified_sessions'
```

Next `dbt run` will reprocess from `snowplow__start_date`.

### Handling Late Data

Configure lookback window:
```yaml
vars:
  snowplow_unified:
    snowplow__upsert_lookback_days: 30    # Re-check last 30 days
    snowplow__days_late_allowed: 3        # Expect data up to 3 days late
```

## Troubleshooting

### Models Not Processing New Data

**Symptoms**: No new rows in derived tables despite new events

**Fixes**:
1. Check manifest: `select * from snowplow_unified_incremental_manifest`
2. Verify `snowplow__start_date` is before your data
3. Confirm events in atomic table: `select count(*) from atomic.events where collector_tstamp >= '2024-01-01'`
4. Check for errors in dbt logs
5. Try full-refresh if stuck: `dbt run --selector snowplow_unified --full-refresh`

### User Stitching Not Working

**Symptoms**: Multiple `user_identifier` values for same person

**Fixes**:
1. Verify user ID fields populated: `select user_id, domain_userid, network_userid from atomic.events where user_id is not null limit 100`
2. Check user_mapping table: `select * from snowplow_unified_user_mapping where user_identifier = 'USER123'`
3. Increase lookback: `snowplow__session_lookback_days: 365`
4. Enable stitching: `snowplow__user_stitching_enabled: true`
5. Full-refresh users model: `dbt run --select snowplow_unified_users --full-refresh`

### Slow Performance

**Fixes**:
1. Reduce backfill: `snowplow__backfill_limit_days: 7` (for dev/testing)
2. Reduce upsert lookback: `snowplow__upsert_lookback_days: 7`
3. Add partitioning on `session_start_tstamp` or `collector_tstamp`
4. Add clustering on `user_identifier`, `session_identifier`
5. Disable unused modules: `snowplow__enable_iab: false`
6. Check warehouse size/concurrency

### Custom Entity Not Appearing

**Symptoms**: Custom entity fields null or missing

**Fixes**:
1. Verify entity in atomic events: `select contexts_com_company_entity_1 from atomic.events where contexts_com_company_entity_1 is not null limit 10`
2. Check `snowplow__entities_or_sdes` configuration
3. Ensure `single_entity: true` for single-valued entities
4. Use correct schema name (check in events table columns)
5. Full-refresh base model: `dbt run --select snowplow_unified_base_events_this_run --full-refresh`

## Testing Strategy

### Data Quality Tests

```yaml
# models/schema.yml
version: 2

models:
  - name: snowplow_unified_sessions
    description: Session-level aggregations
    tests:
      - dbt_utils.recency:
          datepart: day
          field: session_start_tstamp
          interval: 1
    columns:
      - name: session_identifier
        tests:
          - unique
          - not_null
      
      - name: session_duration_s
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: true
      
      - name: page_views
        tests:
          - dbt_utils.accepted_range:
              min_value: 1
              inclusive: true
```

### Volume Monitoring

```sql
-- models/tests/event_volume_check.sql
with daily_events as (
  select
    date_trunc('day', collector_tstamp) as event_date,
    count(*) as event_count
  from {{ ref('snowplow_unified_events') }}
  where collector_tstamp >= current_date - 7
  group by 1
)

select *
from daily_events
where event_count < 1000  -- Alert if below threshold
```

## Resources

**Unified package**: See `references/unified_package.md` for complete configuration
**Configuration**: See `references/configuration.md` for all variables
**Custom models**: See `references/custom_models.md` for patterns and examples
**Performance**: See `references/performance.md` for optimization strategies