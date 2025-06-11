#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# Properties to remove from Postman files
METADATA_PROPERTIES = {
    '_postman_id',
    '_exporter_id',
    'id',
    'uid',
    'owner',
    'createdAt',
    'updatedAt',
    'lastUpdatedBy',
    'lastRevision',
}

# Required schema versions for Postman files
COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
ENVIRONMENT_SCHEMA = "https://schema.getpostman.com/json/environment/v1.0.0/environment.json"

def validate_file(file_path: Path) -> bool:
    """Validate that a Postman file can be processed by the sanitize script."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Preserve the original schema (just check if we can access it)
        original_schema = data.get('info', {}).get('schema') if 'info' in data else data.get('schema')
        
        # Check if it's a valid JSON file with the expected structure
        if file_path.name.endswith('.postman_collection.json'):
            if not isinstance(data, dict):
                print(f"Error: {file_path} is not a valid JSON object", file=sys.stderr)
                return False
            if 'info' not in data or 'item' not in data:
                print(f"Error: {file_path} is missing required 'info' or 'item' fields", file=sys.stderr)
                return False
        elif file_path.name.endswith('.postman_environment.json'):
            if not isinstance(data, dict):
                print(f"Error: {file_path} is not a valid JSON object", file=sys.stderr)
                return False
            if 'id' not in data or 'name' not in data or 'values' not in data:
                print(f"Error: {file_path} is missing required 'id', 'name', or 'values' fields", file=sys.stderr)
                return False
        else:
            print(f"Unknown file type: {file_path}", file=sys.stderr)
            return False
        
        return True
    except json.JSONDecodeError as e:
        print(f"Error: {file_path} is not valid JSON: {str(e)}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error validating {file_path}: {str(e)}", file=sys.stderr)
        return False

def find_postman_files(directory: Path) -> list[Path]:
    """Find all Postman collection and environment files in the directory."""
    patterns = ['*.postman_collection.json', '*.postman_environment.json']
    files = []
    for pattern in patterns:
        files.extend(directory.rglob(pattern))
    return files

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_postman.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist", file=sys.stderr)
        sys.exit(1)
    
    all_valid = True
    for file_path in find_postman_files(directory):
        if not validate_file(file_path):
            all_valid = False
    
    sys.exit(0 if all_valid else 1)

if __name__ == '__main__':
    main() 