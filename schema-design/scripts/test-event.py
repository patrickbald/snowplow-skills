#!/usr/bin/env python3
"""
Send test events to Snowplow collector for validation.
"""

import argparse
import json
import sys
import time
import uuid
from urllib.parse import urlencode
import urllib.request
from typing import Dict, Optional

def generate_event_payload(schema: str, data: Dict, context: Optional[list] = None) -> Dict:
    """Generate a Snowplow event payload."""
    
    # Create self-describing event
    event = {
        "schema": "iglu:com.snowplowanalytics.snowplow/unstruct_event/jsonschema/1-0-0",
        "data": {
            "schema": schema,
            "data": data
        }
    }
    
    # Base payload
    payload = {
        "e": "ue",  # Unstructured event
        "ue_pr": json.dumps(event),
        "tv": "py-test-0.1.0",  # Tracker version
        "p": "srv",  # Platform (server)
        "aid": "test-app",  # App ID
        "eid": str(uuid.uuid4()),  # Event ID
        "dtm": str(int(time.time() * 1000)),  # Device timestamp
        "stm": str(int(time.time() * 1000)),  # Sent timestamp
    }
    
    # Add context if provided
    if context:
        context_payload = {
            "schema": "iglu:com.snowplowanalytics.snowplow/contexts/jsonschema/1-0-1",
            "data": context
        }
        payload["co"] = json.dumps(context_payload)
    
    return payload

def send_event(collector_url: str, payload: Dict, verbose: bool = False) -> bool:
    """Send event to Snowplow collector."""
    
    # Ensure https://
    if not collector_url.startswith("http"):
        collector_url = f"https://{collector_url}"
    
    # Build GET request URL
    url = f"{collector_url}/i?" + urlencode(payload)
    
    if verbose:
        print(f"Sending request to: {collector_url}")
        print(f"Event ID: {payload['eid']}")
        print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                if verbose:
                    print("✅ Event sent successfully")
                return True
            else:
                print(f"❌ Unexpected response status: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Send test events to Snowplow collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send simple event
  python test_event.py \\
    --collector collector.example.com \\
    --schema "iglu:com.company/event/jsonschema/1-0-0" \\
    --data '{"property": "value"}'
  
  # Send event with context
  python test_event.py \\
    --collector collector.example.com \\
    --schema "iglu:com.company/product_viewed/jsonschema/1-0-0" \\
    --data '{"product_id": "PROD-123"}' \\
    --context '[{"schema": "iglu:com.company/user/jsonschema/1-0-0", "data": {"user_id": "user-456"}}]'
        """
    )
    
    parser.add_argument(
        "--collector",
        required=True,
        help="Snowplow collector URL (e.g., collector.example.com)"
    )
    
    parser.add_argument(
        "--schema",
        required=True,
        help="Event schema in Iglu format (e.g., iglu:com.company/event/jsonschema/1-0-0)"
    )
    
    parser.add_argument(
        "--data",
        required=True,
        help="Event data as JSON string"
    )
    
    parser.add_argument(
        "--context",
        help="Context entities as JSON array string"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Parse data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in --data: {str(e)}")
        sys.exit(1)
    
    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
            if not isinstance(context, list):
                print("❌ --context must be a JSON array")
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in --context: {str(e)}")
            sys.exit(1)
    
    # Generate and send event
    payload = generate_event_payload(args.schema, data, context)
    success = send_event(args.collector, payload, args.verbose)
    
    if success:
        print("\n✅ Test event sent successfully!")
        print(f"Event ID: {payload['eid']}")
        print("\nNext steps:")
        print("  1. Check collector logs for event ingestion")
        print("  2. Verify event appears in your data warehouse")
        print("  3. Confirm schema validation passed")
        sys.exit(0)
    else:
        print("\n❌ Failed to send test event")
        sys.exit(1)

if __name__ == "__main__":
    main()