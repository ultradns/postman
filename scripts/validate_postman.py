#!/usr/bin/env python3

import json
import os
import sys
import requests
from pathlib import Path
from jsonschema import validate, RefResolver

# Required schema versions for Postman files
COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
ENVIRONMENT_SCHEMA = "https://schema.getpostman.com/json/environment/v1.0.0/environment.json"

def fetch_schema(url: str) -> dict:
    """Fetch a JSON schema from a URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def validate_file(file_path: Path) -> bool:
    """Validate a single Postman file against its schema."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine which schema to use based on the file type
        if file_path.name.endswith('.postman_collection.json'):
            schema = fetch_schema(COLLECTION_SCHEMA)
        elif file_path.name.endswith('.postman_environment.json'):
            schema = fetch_schema(ENVIRONMENT_SCHEMA)
        else:
            print(f"Unknown file type: {file_path}", file=sys.stderr)
            return False
        
        # Validate the file against the schema
        validate(instance=data, schema=schema)
        return True
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