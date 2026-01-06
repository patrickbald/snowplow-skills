#!/usr/bin/env python3
"""
Validate Snowplow JSON schemas for syntax and best practices.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

def validate_iglu_structure(schema: Dict) -> List[str]:
    """Validate Iglu-specific schema structure."""
    errors = []
    
    # Check for required top-level fields
    if "$schema" not in schema:
        errors.append("Missing required field: $schema")
    elif schema["$schema"] != "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#":
        errors.append("Invalid $schema value")
    
    if "self" not in schema:
        errors.append("Missing required field: self")
    else:
        self_desc = schema["self"]
        required_self_fields = ["vendor", "name", "format", "version"]
        for field in required_self_fields:
            if field not in self_desc:
                errors.append(f"Missing required self field: {field}")
        
        # Validate version format
        if "version" in self_desc:
            version = self_desc["version"]
            if not re.match(r'^\d+-\d+-\d+$', version):
                errors.append(f"Invalid version format: {version}. Must be MODEL-REVISION-ADDITION (e.g., 1-0-0)")
        
        # Validate name format (snake_case)
        if "name" in self_desc:
            name = self_desc["name"]
            if not re.match(r'^[a-z][a-z0-9_]*$', name):
                errors.append(f"Invalid name format: {name}. Use snake_case (e.g., product_viewed)")
    
    return errors

def validate_properties(schema: Dict) -> List[str]:
    """Validate property definitions and constraints."""
    errors = []
    
    if "properties" not in schema:
        errors.append("Schema missing 'properties' field")
        return errors
    
    properties = schema["properties"]
    
    for prop_name, prop_def in properties.items():
        # Check property naming convention
        if not re.match(r'^[a-z][a-z0-9_]*$', prop_name):
            errors.append(f"Property '{prop_name}' should use snake_case")
        
        # Check for description
        if "description" not in prop_def:
            errors.append(f"Property '{prop_name}' missing description")
        
        # Check type-specific constraints
        prop_type = prop_def.get("type")
        
        if prop_type == "string":
            if "maxLength" not in prop_def and "enum" not in prop_def:
                errors.append(f"String property '{prop_name}' should have maxLength or enum constraint")
        
        elif prop_type == "number" or prop_type == "integer":
            if "minimum" not in prop_def and "maximum" not in prop_def:
                errors.append(f"Numeric property '{prop_name}' should have minimum or maximum constraint")
        
        elif prop_type == "array":
            if "items" not in prop_def:
                errors.append(f"Array property '{prop_name}' missing items definition")
            if "maxItems" not in prop_def:
                errors.append(f"Array property '{prop_name}' should have maxItems constraint")
    
    return errors

def validate_best_practices(schema: Dict) -> List[str]:
    """Validate against Snowplow best practices."""
    warnings = []
    
    # Check for additionalProperties
    if schema.get("additionalProperties") is not False:
        warnings.append("Consider setting 'additionalProperties: false' to prevent undocumented fields")
    
    # Check for required fields
    if "required" not in schema or not schema["required"]:
        warnings.append("No required fields specified. Consider which fields should be required")
    
    # Check event naming pattern (object_action)
    if "self" in schema and "name" in schema["self"]:
        name = schema["self"]["name"]
        if "_" in name:
            parts = name.split("_")
            if len(parts) == 2:
                object_part, action_part = parts
                # Check if action part looks like a past tense verb
                if not action_part.endswith(("ed", "ted", "ned")):
                    warnings.append(f"Event name '{name}' - consider using past tense for action (e.g., '{object_part}_viewed')")
    
    return warnings

def validate_schema_file(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a schema file and return success status, errors, and warnings."""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {str(e)}"], []
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"], []
    
    # Run validations
    errors.extend(validate_iglu_structure(schema))
    errors.extend(validate_properties(schema))
    warnings.extend(validate_best_practices(schema))
    
    return len(errors) == 0, errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_schema.py <schema_file.json>")
        print("\nValidates Snowplow JSON schema for:")
        print("  - Iglu structure requirements")
        print("  - Property constraints and best practices")
        print("  - Naming conventions")
        sys.exit(1)
    
    schema_file = sys.argv[1]
    
    print(f"Validating schema: {schema_file}\n")
    
    success, errors, warnings = validate_schema_file(schema_file)
    
    if errors:
        print("❌ ERRORS:")
        for error in errors:
            print(f"  • {error}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    if success and not warnings:
        print("✅ Schema validation passed!")
        sys.exit(0)
    elif success:
        print("✅ Schema validation passed with warnings")
        sys.exit(0)
    else:
        print("❌ Schema validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()