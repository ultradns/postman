#!/usr/bin/env python3

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Set
from jsonschema import validate

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

def fetch_schema(url: str) -> dict:
    """Fetch a JSON schema from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch schema from {url}: {str(e)}", file=sys.stderr)
        return None

def validate_environment(data: dict) -> bool:
    """Validate a Postman environment file has the required fields."""
    if not isinstance(data, dict):
        print("Error: Environment file must be a JSON object", file=sys.stderr)
        return False
    
    if 'name' not in data:
        print("Error: Environment file must have a 'name' field", file=sys.stderr)
        return False
    
    if 'values' not in data:
        print("Error: Environment file must have a 'values' field", file=sys.stderr)
        return False
    
    if not isinstance(data['values'], list):
        print("Error: Environment 'values' field must be an array", file=sys.stderr)
        return False
    
    return True

def validate_file(file_path: Path) -> bool:
    """Validate that a Postman file can be processed by the sanitize script."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Just check if it's valid JSON and can be processed
        if not isinstance(data, dict):
            print(f"Error: {file_path} is not a valid JSON object", file=sys.stderr)
            return False
        
        # Validate based on file type
        if file_path.name.endswith('.postman_collection.json'):
            schema = fetch_schema(COLLECTION_SCHEMA)
            if schema:
                validate(instance=data, schema=schema)
        elif file_path.name.endswith('.postman_environment.json'):
            if not validate_environment(data):
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
    files = find_postman_files(directory)
    
    if not files:
        print("No Postman files found to validate")
        sys.exit(0)
    
    for file_path in files:
        if not validate_file(file_path):
            all_valid = False
    
    if all_valid:
        print("✅ All Postman files are valid")
    
    sys.exit(0 if all_valid else 1)

if __name__ == '__main__':
    main() 